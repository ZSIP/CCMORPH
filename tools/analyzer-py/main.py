import re
import json
import glob
from natsort import natsorted
import pandas as pd
import geopandas as gpd
import numpy as np
from os import makedirs
from os.path import join, basename, exists
from halo import Halo as spiner

from analyzer import get_volume, get_distance, get_slope

# get config
with open("config.json", "r") as jsonfile:
    config = json.load(jsonfile)

csv_profiles = config["csv"]["profiles"]
csv_points = config["csv"]["points"]
csv_output = config["csv"]["output"]

points_input_path = join(config["paths"]["base"], config["paths"]["input"]["points"])
points_first_file = join(
    points_input_path, csv_points["first"]
)  # main file if more fils
profiles_input_path = join(
    config["paths"]["base"], config["paths"]["input"]["profiles"]
)
shapes_output_path = join(config["paths"]["base"], config["paths"]["output"]["shapes"])

# all or selected profiles?
selected = True if len(config["selected_profiles"]) > 0 else False

# get distance between transects => profiles width
db_file = join(config["paths"]["base"], config["paths"]["db"])
points = gpd.read_file(db_file, layer="points")
points_distance = round(points.iloc[0].geometry.distance(points.iloc[1].geometry), 3)

# load CSV files conaining bottom and top points
point_files = natsorted(glob.glob(f"{points_input_path}/*.csv"))  # todo
points = pd.read_csv(
    points_first_file,
    encoding="utf-8",
    sep=csv_points["sep"],
    skipinitialspace=True,  # todo
)
point_files.remove(points_first_file)
for file in point_files:
    next_points = pd.read_csv(
        file,
        encoding="utf-8",
        sep=csv_points["sep"],
        skipinitialspace=True,
        names=csv_points["colnames"],
    )
    points = pd.concat([points, next_points])
points = points.dropna(subset=["bottom", "top"])  # remove rows with NaN bottom & top

# list profile files
profile_files = natsorted(glob.glob(f"{profiles_input_path}/*.csv"))  # todo
profile_files_count = len(profile_files)
counter = 0

# loop through the profiles folder
print("... calculation of profile properties")
results = pd.DataFrame()
for name in profile_files:
    with spiner(
        text=f"{counter} / {profile_files_count} -> {basename(name)}", spinner="dots"
    ):
        counter += 1
        # get profile number from file name
        profile_id = int(re.findall("\d{1,4}", basename(name))[0])

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
                # if method != 0: # 0 - manual
                #     break
                break
        method = -1

        # todo:
        # if len(correct_points):
        #     correct_points = correct_points[correct_points.method == correct_points.iloc[0].method]
        #     if len(correct_points) > 1:
        #         m_top, m_bottom = correct_points.top.median(axis = 0), correct_points.bottom.median(axis = 0)
        #         correct_points = correct_points[abs(correct_points.top - m_top) < config["max_error"]]
        #         correct_points = correct_points[abs(correct_points.bottom - m_bottom) < config["max_error"]]
        #         if len(correct_points):
        #             m_top, m_bottom = round(correct_points.top.median(axis = 0)), round(correct_points.bottom.median(axis = 0))

        if len(correct_points) == 0:
            continue
        else:
            top_id = int(correct_points.iloc[0].top)
            bottom_id = int(correct_points.iloc[0].bottom)
            first_zero_id = int(correct_points.iloc[0].first_zero)
            last_zero_id = int(correct_points.iloc[0].last_zero)
        # top_id = m_top if len(correct_points) > 1 else int(correct_points.iloc[0].top)
        # bottom_id = m_bottom if len(correct_points) > 1 else int(correct_points.iloc[0].bottom)

        bottom = csv[csv.no_point == bottom_id]
        top = csv[csv.no_point == top_id]
        first_zero = csv[csv.no_point == first_zero_id]
        last_zero = csv[csv.no_point == last_zero_id]

        result = {
            "profile_id": profile_id,
            "method": correct_points.iloc[0].method,
            "first_zero_id": first_zero_id,
            "last_zero_id": last_zero_id,
            "bottom_id": bottom_id,
            "top_id": top_id,
            "first_zero_x": (
                first_zero.x_geo.values[0] if len(first_zero) > 0 else np.nan
            ),
            "first_zero_y": (
                first_zero.y_geo.values[0] if len(first_zero) > 0 else np.nan
            ),
            "first_zero_elevation": (
                first_zero.elevation.values[0] if len(first_zero) > 0 else np.nan
            ),
            "last_zero_x": last_zero.x_geo.values[0] if len(last_zero) > 0 else np.nan,
            "last_zero_y": last_zero.y_geo.values[0] if len(last_zero) > 0 else np.nan,
            "last_zero_elevation": (
                last_zero.elevation.values[0] if len(last_zero) > 0 else np.nan
            ),
            "bottom_x": bottom.x_geo.values[0] if len(bottom) > 0 else np.nan,
            "bottom_y": bottom.y_geo.values[0] if len(bottom) > 0 else np.nan,
            "bottom_elevation": (
                bottom.elevation.values[0] if len(bottom) > 0 else np.nan
            ),
            "top_x": top.x_geo.values[0] if len(top) > 0 else np.nan,
            "top_y": top.y_geo.values[0] if len(top) > 0 else np.nan,
            "top_elevation": top.elevation.values[0] if len(top) > 0 else np.nan,
            "to_bottom_distance": get_distance(csv, first_zero_id, bottom_id),
            "to_bottom_slope": get_slope(csv, first_zero_id, bottom_id),
            "to_bottom_volume": get_volume(
                points_distance, csv, first_zero_id, bottom_id, True
            ),
            "to_top_distance": get_distance(csv, bottom_id, top_id),
            "to_top_slope": get_slope(csv, bottom_id, top_id),
            "to_top_volume": get_volume(points_distance, csv, bottom_id, top_id, True),
        }

        results = pd.concat([results, pd.DataFrame([result])])

# save CSV
print("... exporting profile properties")
results.to_csv(
    join(
        config["paths"]["base"],
        config["paths"]["output"]["finall"],
        csv_output["first"],
    ),
    sep=csv_output["sep"],
)

# save SHP
print("... exporting SHP data (the base and the top points)")


if not exists(shapes_output_path):
    makedirs(shapes_output_path)

bottom_points = gpd.GeoDataFrame(
    results[["profile_id", "bottom_id", "method", "bottom_elevation"]],
    geometry=gpd.points_from_xy(results.bottom_x, results.bottom_y),
)
bottom_points.rename(
    columns={"bottom_elevation": "elevation", "bottom_id": "point_id"}, inplace=True
)
top_points = gpd.GeoDataFrame(
    results[["profile_id", "top_id", "method", "top_elevation"]],
    geometry=gpd.points_from_xy(results.top_x, results.top_y),
)
top_points.rename(
    columns={"top_elevation": "elevation", "top_id": "point_id"}, inplace=True
)
first_zero_points = gpd.GeoDataFrame(
    results[["profile_id", "first_zero_id", "first_zero_elevation"]],
    geometry=gpd.points_from_xy(results.first_zero_x, results.first_zero_y),
)
first_zero_points.rename(
    columns={"first_zero_elevation": "elevation", "first_zero_id": "point_id"},
    inplace=True,
)
last_zero_points = gpd.GeoDataFrame(
    results[["profile_id", "last_zero_id", "last_zero_elevation"]],
    geometry=gpd.points_from_xy(results.last_zero_x, results.last_zero_y),
)
last_zero_points.rename(
    columns={"last_zero_elevation": "elevation", "last_zero_id": "point_id"},
    inplace=True,
)

bottom_points.set_crs(crs=config["shape"]["crs"]).to_file(
    join(shapes_output_path, "bottomPoints")
)
top_points.set_crs(crs=config["shape"]["crs"]).to_file(
    join(shapes_output_path, "topPoints")
)
first_zero_points.set_crs(crs=config["shape"]["crs"]).to_file(
    join(shapes_output_path, "firstZeroPoints")
)
last_zero_points.set_crs(crs=config["shape"]["crs"]).to_file(
    join(shapes_output_path, "lastZeroPoints")
)
