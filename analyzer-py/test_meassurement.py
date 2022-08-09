import re
import json
import glob
from natsort import natsorted
import pandas as pd
import numpy as np

from analyzer import get_points_by_elevation, get_volume, get_distance, get_slope

# get config
with open("config.json", "r") as jsonfile:
    config = json.load(jsonfile)
csv_profiles = config["csv"]["profiles"]

# all or selected profiles?
selected = True if len(config["selected_profiles"]) > 0 else False

# list profile files
profile_files = natsorted(glob.glob(f'{str(csv_profiles["path"])}/*.csv'))
profile_files_count = len(profile_files)
counter = 0

# loop through the profiles folder
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

    # check if any profile points are located in the selected area (index_right == 1.0)
    cut = csv[csv["id"] > 0]
    if len(cut) == 0:
        continue
    first_no = cut.iloc[0]["no_point"]
    last_no = cut.iloc[-1]["no_point"]

    # test elevation points
    test_points = get_points_by_elevation([0, 1], csv, first_no, last_no)

    # test volume
    print(
        f"\n{profile_id} volume (absolute) {first_no} - {last_no} : {get_volume(1, csv, first_no, last_no, True)}"
    )
    print(
        f"{profile_id} volume (relative) {first_no} - {last_no} : {get_volume(1, csv, first_no, last_no, False)}"
    )

    # test distance
    print(
        f"{profile_id} distance {first_no} - {last_no} : {get_distance(csv, first_no, last_no)}"
    )

    # test slope
    print(
        f"{profile_id} slope {first_no} - {last_no} : {get_slope(csv, first_no, last_no)}"
    )