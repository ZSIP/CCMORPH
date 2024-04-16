import json
import glob
import ast
import warnings
import pandas as pd
import geopandas as gpd
from osgeo import gdal, gdalconst
from copy import deepcopy
from os.path import join, basename, splitext
import pgen.config as config


def export_profiles(cfg):
    export_geojson(cfg)
    export_names(cfg)


def export_geojson(cfg):
    (
        cropped_path,
        geotiff_path,
        geojson_path,
        buffer_path,
        db,
        profiles_layer,
        buffer_crs,
        cropped_dem_crs,
        export_crs,
        geojson_template_json,
    ) = config.parse(cfg, export_geojson.__name__)

    try:
        cropped_profiles = crop_profiles(
            db, profiles_layer, buffer_path, buffer_crs, export_crs
        )
        geojson_template = ast.literal_eval(geojson_template_json)

        for path in sorted(glob.glob(join(cropped_path, "*.tif")), key=len):
            file_name, file_extension = splitext(basename(path))
            output = join(geotiff_path, f"{file_name}_wgs84.tif")
            dem = gdal.Open(path, gdal.GA_ReadOnly)
            options = gdal.WarpOptions(
                srcSRS=cropped_dem_crs,
                dstSRS=export_crs,
                format="GTiff",
                resampleAlg="near",
                outputType=gdalconst.GDT_Float32,
            )
            gdal.Warp(output, dem, options=options)

            data = gdal.Open(output, gdal.GA_ReadOnly)
            geo_transform = data.GetGeoTransform()
            min_x = geo_transform[0]
            max_y = geo_transform[3]
            max_x = min_x + geo_transform[1] * data.RasterXSize
            min_y = max_y + geo_transform[5] * data.RasterYSize
            with open(join(geotiff_path, f"{file_name}_bbox.json"), "w") as bbox_file:
                json.dump({"bbox": [[min_y, min_x], [max_y, max_x]]}, bbox_file)
            data = None

            name_parts = file_name.split("_")
            dem_idx = name_parts[0]
            dem_name = "_".join(name_parts[1:]).replace("crop_", "")

            filtered_profiles = cropped_profiles.query(
                f"no_transect=={dem_idx} and dem=='{dem_name}.tif'"
            )
            geojson = deepcopy(geojson_template)
            geojson["name"] = f"{file_name}.geojson"
            if len(filtered_profiles) > 0:
                geojson["properties"]["firstPoint"] = int(
                    filtered_profiles.iloc[0].no_point
                )
            # "geojson_template": "{'name': '','type': 'FeatureCollection','features': [{'type': 'Feature','geometry': {'type': 'LineString','coordinates':[]}}], 'properties': {'firstPoint': 0}}"

            for idx, row in filtered_profiles.iterrows():
                geojson["features"][0]["geometry"]["coordinates"].append(
                    [row["x"], row["y"], row["elevation"]]
                )
            if len(geojson["features"][0]["geometry"]["coordinates"]) > 0:
                with open(
                    join(geojson_path, f"{file_name}.geojson"), "w"
                ) as geojson_file:
                    json.dump(geojson, geojson_file)
    except Exception as e:
        print("... export_geojson function error")
        raise e


def crop_profiles(db, profiles_layer, buffer_path, buffer_crs, export_crs):
    profiles = gpd.read_file(db, layer=profiles_layer["name"], index="dem").to_crs(
        buffer_crs
    )

    cropping_buffer = gpd.read_file(glob.glob(join(buffer_path, "*.shp"))[0]).to_crs(
        buffer_crs
    )
    if "id" not in cropping_buffer.keys():
        cropping_buffer.insert(0, "id", [1])

    cropped_profiles = gpd.sjoin(
        profiles, cropping_buffer, predicate="within", how="left"
    ).set_crs(buffer_crs)
    cropped_profiles = cropped_profiles[~cropped_profiles.isna().id].to_crs(export_crs)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=".*Geometry is in a geographic CRS\. Results from 'centroid' are likely incorrect.*",
        )
        cropped_profiles = cropped_profiles.assign(x=cropped_profiles.centroid.x)
        cropped_profiles = cropped_profiles.assign(y=cropped_profiles.centroid.y)
    cropped_profiles.drop_duplicates(inplace=True)

    return cropped_profiles


def export_names(cfg):
    geojson_path, names_path = config.parse(cfg, export_names.__name__)

    try:
        path_list = glob.glob(join(geojson_path, "*.geojson"))
        file_list = list(map(lambda e: splitext(basename(e))[0], path_list))

        with open(join(names_path, "names.json"), "w") as file:
            json.dump({"names": file_list}, file)
    except Exception as e:
        print("... export_names function error")
        raise e
