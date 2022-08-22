import re
import json
import glob
from natsort import natsorted
import pandas as pd
import numpy as np
from os.path import join, isdir, basename
from os import mkdir, remove
from halo import Halo as spiner

from shaper import smooth_profile, get_main_points

pd.options.mode.chained_assignment = None

# get config
with open("config.json", "r") as jsonfile:
    config = json.load(jsonfile)
paths = config["paths"]
csv_profiles = config["csv"]["profiles"]
debug_path = config["debug"]["path"]
method = config["method"]

if not isdir(debug_path):
    mkdir(debug_path)
else:
    files = glob.glob(join(debug_path, "*"))
    for file in files:
        remove(file)

# all or selected profiles?
selected = True if len(config["selected_profiles"]) > 0 else False

# list of obtained results
results = []

# list profile files
profile_files = natsorted(glob.glob(f'{str(paths["input"]["profiles"])}/*.csv'))
profile_files_count = len(profile_files)
counter = 0

# loop through the profiles folder
for name in profile_files:
    with spiner(text=f"{counter} / {profile_files_count} -> {basename(name)}", spinner="dots"):
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

        # check if any profile points are located in the selected area (id == 1.0)
        cut = csv[csv["id"] > 0]
        # print(f'{profile_id}   {len()}  {len()}')
        if len(cut) == 0:
            continue
        first_no = cut.iloc[0]["no_point"]
        last_no = cut.iloc[-1]["no_point"]

        # find base and top points
        if config["smoothness"]["use"]:
            smooth = smooth_profile(csv, first_no, last_no)
            if type(smooth) != type(None):
                csv.elevation[first_no:last_no] = np.array(smooth)
            else:
                continue

        if method == 1:
            result = get_main_points(
                csv,
                first_no,
                last_no,
                method=1,
                profile_id=profile_id,
                min_profile_points=20,
                elevation_threshold=3,
                debug=config["debug"]["use"],
            )
        else:
            result = get_main_points(
                csv, first_no, last_no, method=2, min_profile_points=20
            )

        results.append(
            {
                "profile_id": profile_id,
                "method": method,
                "smooth": config["smoothness"]["use"],
                "bottom": result["bottom"],                
                "top": result["top"],
            }
        )

        # save debug file for the profile
        if config["debug"]["use"]:
            debug_file = join(debug_path, f"M1_profile_{profile_id}_debug.csv")
            result["debug"].to_csv(debug_file)

# export results to CSV file/files (all profiles together)
output = paths["output"]["results"]
files = output if isinstance(output, list) else [output]
for file in files:
    pd.DataFrame(results).to_csv(
        file, sep=config["csv"]["output"]["sep"], index=False, encoding='utf-8'
    )
