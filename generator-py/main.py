# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 20:18:51 2021
@author: ałysko, pforczmański, wmackow
geopackage database.gpkg can be opened in QGIS
"""

import json
import pgen

# get config
with open("config.json", "r") as jsonfile:
    config = json.load(jsonfile)

try:
    # check input and db paths and create output paths
    print("... initializing data structures")
    pgen.init(config)

    # generate transects
    print("... generating transects")
    pgen.generate_transects(config)

    # get DEM around transects
    print("... preparing cropped DEM rasters")
    pgen.get_DEM(config)

    # generate profiles
    print("... generating profiles")
    pgen.generate_profiles(config)

    # crop profiles
    print(f"... cropping profiles")
    pgen.crop_profiles(config)

    # export data for a web tool
    print("... exporting data for a web application")
    pgen.export_profiles(config)

except Exception as e:
    print(f"{type(e)}: {e}")
