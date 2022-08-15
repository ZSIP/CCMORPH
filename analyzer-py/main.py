import re
import json
import glob
from natsort import natsorted
import pandas as pd
import geopandas as gpd
from os.path import join

from analyzer import get_points_by_elevation, get_volume, get_distance, get_slope

# get config
with open("config.json", "r") as jsonfile:
    config = json.load(jsonfile)
csv_profiles = config["csv"]["profiles"]
csv_points = config["csv"]["points"]
csv_output = config["csv"]["output"]

# all or selected profiles?
selected = True if len(config["selected_profiles"]) > 0 else False

# load CSV files conaining bottom and top points
point_files = natsorted(glob.glob(f'{str(csv_points["path"])}/*.csv'))
points = pd.read_csv(
    join(csv_points["path"], csv_points["first"]), encoding="utf-8", sep=csv_points["sep"], skipinitialspace=True
)
for file in point_files:
    next_points = pd.read_csv(
        file, encoding="utf-8", sep=csv_points["sep"], skipinitialspace=True, names=csv_points["colnames"]
    )
    points = pd.concat([points, next_points])
points = points.dropna(subset=['bottom','top']) # remove rows with NaN bottom & top

# list profile files
profile_files = natsorted(glob.glob(f'{str(csv_profiles["path"])}/*.csv'))
profile_files_count = len(profile_files)
counter = 0

# loop through the profiles folder
results = pd.DataFrame()
for name in profile_files:
    counter += 1
    # get profile number from file name
    profile_id = int(re.findall("\d{1,4}", name)[0])

    # analyze all or selected profiles?
    if selected:
        if profile_id not in config["selected_profiles"]:
            continue

    # read CSV profile file
    csv = pd.read_csv(
        name, encoding="utf-8", sep=csv_profiles["sep"], skipinitialspace=True
    )

    # select points by profile id
    profile_points = points[points.profile_id == profile_id]
    correct_points = pd.DataFrame()
    for method in config["methods_order"]:
        tmp_points = profile_points[profile_points.method == method]
        if len(tmp_points):
            correct_points = pd.concat([correct_points, tmp_points])
            if method != 0: # 0 - manual
                break
    method = -1
    if len(correct_points):
        correct_points = correct_points[correct_points.method == correct_points.iloc[0].method]
        if len(correct_points) > 1:
            m_top, m_bottom = correct_points.top.median(axis = 0), correct_points.bottom.median(axis = 0)
            correct_points = correct_points[abs(correct_points.top - m_top) < config["max_error"]]
            correct_points = correct_points[abs(correct_points.bottom - m_bottom) < config["max_error"]]
            if len(correct_points):
                m_top, m_bottom = round(correct_points.top.median(axis = 0)), round(correct_points.bottom.median(axis = 0))
    
    if len(correct_points) == 0:
        continue

    top_id = m_top if len(correct_points) > 1 else int(correct_points.iloc[0].top)
    bottom_id = m_bottom if len(correct_points) > 1 else int(correct_points.iloc[0].bottom)

    bottom = csv[csv.no_point == bottom_id]
    top = csv[csv.no_point == top_id]

    result = {
        "profile_id": profile_id,
        "bottom_id": bottom_id,
        "top_id": top_id,
        "distance": get_distance(csv, bottom_id, top_id),
        "slope": get_slope(csv, bottom_id, top_id),
        "volume": get_volume(1, csv, bottom_id, top_id, True),
        "method": correct_points.iloc[0].method,
        "bottom_x": bottom.x_geo.values[0],
        "bottom_y": bottom.y_geo.values[0],
        "bottom_elevation": bottom.elevation.values[0],
        "top_x": top.x_geo.values[0],
        "top_y": top.y_geo.values[0],
        "top_elevation": top.elevation.values[0]
    }

    results = pd.concat([results, pd.DataFrame([result])])

# save CSV
results.to_csv(join(csv_output["path"], csv_output["first"]), sep=csv_output["sep"])

# save SHP
bottom_points = gpd.GeoDataFrame(results[["profile_id", "bottom_id", "method", "bottom_elevation"]], geometry=gpd.points_from_xy(results.bottom_x, results.bottom_y))
bottom_points.rename(columns = {'bottom_elevation':'elevation'}, inplace = True)
top_points = gpd.GeoDataFrame(results[["profile_id", "top_id", "method", "top_elevation"]], geometry=gpd.points_from_xy(results.top_x, results.top_y))
top_points.rename(columns = {'top_elevation':'elevation'}, inplace = True)

bottom_points.to_file(join(config["shape"]["path"], "bottomPoints"), crs=config["shape"]["crs"])
top_points.to_file(join(config["shape"]["path"], "topPoints"), crs=config["shape"]["crs"])
