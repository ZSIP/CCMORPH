import glob
import shutil
import geopandas as gpd
from os.path import exists, isdir, join, dirname
from os import makedirs, remove


def init(config):
    check_paths(config["paths"])
    read_coastline(config)


def check_paths(config_paths):
    base = config_paths["base"]

    check_base_path(base)
    check_input_path(base, config_paths["input"])
    check_db_path(base, config_paths["db"])
    check_output_path(base, config_paths["output"])


def check_base_path(base):
    if not exists(base):
        raise Exception(
            1001,
            f"... paths error: base path cannot be located ({base}). Check config.json.",
        )
    if not isdir(base):
        raise Exception(
            f"... paths error: base path ({base}) is not a directory. Check config.json."
        )


def check_input_path(base, input):
    paths = list(input.values())
    for path in paths:
        inpath = join(base, path)
        if not exists(inpath):
            raise Exception(
                f"... paths error: one of input paths cannot be located ({inpath}). Check config.json."
            )
        if not isdir(inpath):
            raise Exception(
                f"... paths error: one of input paths ({inpath}) is not a directory. Check config.json."
            )


def check_db_path(base, db):
    dbpath = join(base, db)
    if exists(dbpath):
        remove(dbpath)
    dir_name = dirname(dbpath)
    if not exists(dir_name):
        makedirs(dir_name)


def check_output_path(base, output):
    paths = list(output.values())
    for path in paths:
        outpath = join(base, path)
        try:
            makedirs(outpath)
        except FileExistsError:
            files = glob.glob(join(outpath, "*"))
            for file in files:
                if isdir(file):
                    shutil.rmtree(file)
                else:
                    remove(file)
        except:
            raise Exception(
                f"... paths error: there is a proble with one of output paths ({outpath}). Check config.json."
            )


def read_coastline(config):
    base = config["paths"]["base"]
    coastline_path = join(base, config["paths"]["input"]["coastline"])
    shapes = glob.glob(join(coastline_path, "*.shp"))

    if len(shapes) > 0:
        line = gpd.read_file(shapes[0]).to_crs(config["shapes"]["coastline"]["dst_crs"])
        line.to_file(
            join(base, config["paths"]["db"]),
            layer=config["db"]["layers"]["coastline"]["name"],
            driver="GPKG",
        )
    else:
        raise Exception(f"... cannot find any coastline SHP file ({coastline_path}).")
