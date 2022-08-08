import glob
import geopandas as gpd
from osgeo import gdal, gdalconst
from os.path import join, basename
import pgen.config as config


def get_DEM(cfg):
    (
        dem_path,
        cropped_path,
        slope_path,
        db,
        transects_layer,
        buffers_layer,
        resolution,
        src_crs,
        dst_crs,
        transect_length,
    ) = config.parse(cfg, get_DEM.__name__)

    try:
        dem_input_files = glob.glob(join(dem_path, "*.tif"))

        transects = gpd.read_file(db, layer=transects_layer["name"]).to_crs(
            transects_layer["crs"]
        )
        buffers = transects.buffer(transect_length / 2, resolution=resolution)
        buffers.to_file(db, layer=buffers_layer["name"], driver="GPKG")
        buffers_count = len(buffers.index)

        for input_file in dem_input_files:
            buffer_idx = 1
            dem_input = gdal.Open(input_file, gdal.GA_ReadOnly)
            while buffer_idx <= buffers_count:
                dem_cropped_file = join(
                    cropped_path, f"{buffer_idx}_crop_{basename(input_file)}"
                )
                options = gdal.WarpOptions(
                    srcSRS=src_crs,
                    dstSRS=dst_crs,
                    format="GTiff",
                    cutlineDSName=db,
                    cutlineLayer=buffers_layer["name"],
                    cutlineWhere=f"fid={buffer_idx}",
                    cropToCutline=True,
                    outputType=gdalconst.GDT_Float32,
                )
                gdal.Warp(dem_cropped_file, dem_input, options=options)

                slope_file = join(
                    slope_path, f"{buffer_idx}_slope_{basename(input_file)}"
                )
                dem_cropped = gdal.Open(dem_cropped_file, gdal.GA_ReadOnly)
                gdal.DEMProcessing(slope_file, dem_cropped, "slope")
                dem_cropped = None

                buffer_idx += 1

    except Exception as e:
        print("... get_DEM function error")
        raise e
