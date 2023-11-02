import glob
import numpy as np
import pandas as pd
import geopandas as gpd
import shapely
from osgeo import gdal
from os.path import join, basename
from math import floor
import pgen.config as config

def reverse_geom(geom):
    def _reverse(x, y, z=None):
        if z:
            return x[::-1], y[::-1], z[::-1]
        return x[::-1], y[::-1]

    return shapely.ops.transform(_reverse, geom)

def generate_profiles(cfg):
    (
        dem_path,
        cropped_path,
        slope_path,
        profile_path,
        db,
        profiles_layer,
        transects_layer,
        height_resolution,
        profile_csv,
    ) = config.parse(cfg, generate_profiles.__name__)

    try:
        dem_input_files = glob.glob(join(dem_path, "*.tif"))

        transects = gpd.read_file(db, layer=transects_layer["name"])
        transects_count = transects.id.count()
        transect_lines = np.asarray(transects.geometry)

        profiles = pd.DataFrame()

        for input_file in dem_input_files:
            repeat = True
            reverse = False

            while repeat:
                transect_idx = 0
                mono = 0
                while transect_idx < transects_count:
                    profile = pd.DataFrame()
                    cropped_file = join(
                        cropped_path, f"{transect_idx + 1}_crop_{basename(input_file)}"
                    )
                    slope_file = join(
                        slope_path, f"{transect_idx + 1}_slope_{basename(input_file)}"
                    )

                    height_raster = gdal.Open(cropped_file)
                    slope_raster = gdal.Open(slope_file)
                    height_array = height_raster.GetRasterBand(1).ReadAsArray()
                    slope_array = slope_raster.GetRasterBand(1).ReadAsArray()
                    height_nodata = height_raster.GetRasterBand(1).GetNoDataValue()

                    env = height_raster.GetGeoTransform()
                    x_origin = env[0]
                    y_origin = env[3]
                    pixel_width = env[1]
                    pixel_height = -env[5]

                    line = transect_lines[transect_idx]
                    if reverse:
                        line = reverse_geom(line)
                    current_dist = 0
                    x, y, dist, elevation, slope, xg, yg = [], [], [], [], [], [], []

                    while current_dist < floor(line.length):
                        dist.append(current_dist)
                        point = line.interpolate(current_dist)
                        col = int((point.x - x_origin) / pixel_width)
                        row = int((y_origin - point.y) / pixel_height)
                        x_geo = point.x
                        y_geo = point.y
                        elevation.append(height_array[row][col])
                        slope.append(slope_array[row][col])
                        x.append(int(row))
                        y.append(int(col))
                        xg.append(float(x_geo))
                        yg.append(float(y_geo))
                        current_dist += height_resolution
                    elevation = list(map(lambda i: 0 if i == height_nodata else i, elevation))
                    # profile = profile.assign(nb=transect_idx, indx=df.index)
                    profile = pd.DataFrame(
                        {
                            "no_transect": transect_idx + 1,
                            "length_transect": line.length,
                            "no_point": dist,
                            "dem": basename(input_file),
                            "x_image": x,
                            "y_image": y,
                            "x_geo": xg,
                            "y_geo": yg,
                            "elevation": [round(num, 2) for num in elevation],
                            "slope": [round(num, 2) for num in slope],
                        }
                    )
                    profile_file = join(
                        profile_path, f"{transect_idx + 1}_whole_{basename(input_file)}"
                    )
                    profile.to_csv(
                        profile_file.replace(".tif", ".csv"),
                        sep=profile_csv["sep"],
                        encoding=profile_csv["encoding"],
                        index=False,
                    )
                    profiles = pd.concat([profiles, profile], ignore_index=True)
                    transect_idx += 1
                    mono += profile.elevation[profile[profile.elevation > 0].index[0]:profile[profile.elevation > 0].index[-1]].diff().sum()
                if mono > 0:
                    repeat = False
                else:
                    reverse = True
            gpd.GeoDataFrame(
                profiles, geometry=gpd.points_from_xy(profiles.x_geo, profiles.y_geo)
            ).set_crs(profiles_layer["crs"]).to_file(
                db, layer=profiles_layer["name"], driver="GPKG", overwrite="yes"
            )
    except Exception as e:
        print("... generate_profiles function error")
        raise e


def crop_profiles(cfg):
    (
        buffer_path,
        in_profile_path,
        out_profile_path,
        buffer_shape,
        in_profile_csv,
        out_profile_csv,
    ) = config.parse(cfg, crop_profiles.__name__)
    try:
        buffers = glob.glob(join(buffer_path, "*.shp"))
        cropping_buffer = gpd.read_file(buffers[0]).to_crs(buffer_shape["dst_crs"])
        cropping_buffer.id = 1 # change id

        profile_files = glob.glob(join(in_profile_path, "*.csv"))

        for source_file in profile_files:

            csv_profile = pd.read_csv(source_file, sep=in_profile_csv["sep"])
            profile = gpd.GeoDataFrame(
                csv_profile,
                geometry=gpd.points_from_xy(csv_profile.x_geo, csv_profile.y_geo),
            ).set_crs(in_profile_csv["crs"])

            cropped_profile = gpd.sjoin(
                profile, cropping_buffer, predicate="within", how="left"
            )
            cropped_profile = cropped_profile.to_crs(out_profile_csv["crs"])
            cropped_profile.to_csv(
                join(out_profile_path, basename(source_file).replace('whole', 'crop')),
                sep=out_profile_csv["sep"],
                encoding=out_profile_csv["encoding"],
                index=False,
            )
    except Exception as e:
        print("... crop_profiles function error")
        raise e
