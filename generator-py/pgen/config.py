from os.path import join, basename


def parse(cfg, fname):
    return eval(f"_{fname}(cfg)")


def _get_DEM(cfg):
    base_path = cfg["paths"]["base"]
    return (
        join(base_path, cfg["paths"]["input"]["dem"]),  # dem_path
        join(base_path, cfg["paths"]["output"]["dem_cropped"]),  # cropped_path
        join(base_path, cfg["paths"]["output"]["dem_slope"]),  # slope_path
        join(base_path, cfg["paths"]["db"]),  # db
        cfg["db"]["layers"]["transects"],  # transects_layer
        cfg["db"]["layers"]["buffers"],  # buffers_layer
        cfg["dem"]["resolution"],  # resolution
        cfg["dem"]["src_crs"],  # src_crs
        cfg["dem"]["dst_crs"],  # dst_crs
        cfg["dem"]["buffer_width"],  # buffer_width
        cfg["transect"]["length"],  # transect_length
    )


def _generate_transects(cfg):
    return (
        join(cfg["paths"]["base"], cfg["paths"]["db"]),  # db
        cfg["db"]["layers"]["coastline"],  # line_layer
        cfg["db"]["layers"]["points"],  # points_layer
        cfg["db"]["layers"]["transects"],  # transects_layer
        cfg["transect"]["distance"],  # transect_distance
        cfg["transect"]["length"],  # transect_length
    )


def _generate_profiles(cfg):
    base_path = cfg["paths"]["base"]
    return (
        join(base_path, cfg["paths"]["input"]["dem"]),  # dem_path
        join(base_path, cfg["paths"]["output"]["dem_cropped"]),  # cropped_path
        join(base_path, cfg["paths"]["output"]["dem_slope"]),  # slope_path
        join(base_path, cfg["paths"]["output"]["profiles_whole"]),  # profile_path
        join(base_path, cfg["paths"]["db"]),  # db
        cfg["db"]["layers"]["profiles"],  # profiles_layer
        cfg["db"]["layers"]["transects"],  # transects_layer
        cfg["profile"]["resolution"],  # resolution
        cfg["csv"]["profile_whole"],  # profile_csv
    )


def _crop_profiles(cfg):
    base_path = cfg["paths"]["base"]
    return (
        join(base_path, cfg["paths"]["input"]["crop"]),  # buffer_path
        join(base_path, cfg["paths"]["output"]["profiles_whole"]),  # in_profile_path
        join(base_path, cfg["paths"]["output"]["profiles_cropped"]),  # out_profile_path
        cfg["shapes"]["buffer"],  # buffer_shape
        cfg["csv"]["profile_whole"],  # in_profile_csv
        cfg["csv"]["profile_cropped"],  # out_profile_csv
    )


def _export_geojson(cfg):
    base_path = cfg["paths"]["base"]
    return (
        join(base_path, cfg["paths"]["output"]["dem_cropped"]),  # cropped_path
        join(base_path, cfg["paths"]["output"]["web_geotiff"]),  # geotiff_path
        join(base_path, cfg["paths"]["output"]["web_geojson"]),  # geojson_path
        join(base_path, cfg["paths"]["input"]["web_crop"]),  # buffer_path
        join(base_path, cfg["paths"]["db"]),  # db
        cfg["db"]["layers"]["profiles"],  # profiles_layer
        cfg["shapes"]["buffer"]["dst_crs"],  # buffer_crs
        cfg["dem"]["dst_crs"],  # cropped_dem_crs
        cfg["export"]["crs"],  # export_crs
        cfg["export"]["geojson_template"],  # geojson_template_json
    )


def _export_names(cfg):
    base_path = cfg["paths"]["base"]
    return (
        join(base_path, cfg["paths"]["output"]["web_geojson"]),  # geojson_path
        join(base_path, cfg["paths"]["output"]["web_names"]),  # names_path
    )
