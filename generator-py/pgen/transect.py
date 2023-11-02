import math
import fiona
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, shape, mapping
import pgen.config as config


def generate_transects(cfg, show_progress=True):
    (
        db,
        line_layer,
        points_layer,
        transects_layer,
        transect_distance,
        transect_length,
    ) = config.parse(cfg, generate_transects.__name__)

    try:
        # generate points on the line (new layer of points in the base, fixed distances between points)
        points_no = line_to_points(
            db,
            line_layer["name"],
            points_layer["name"],
            line_layer["crs"],
            transect_distance,
        )
        points = gpd.read_file(db, layer=points_layer["name"])
        points.set_crs(points_layer["crs"], inplace=True, allow_override=True)

        transects_tmp = pd.DataFrame()

        i = 0
        while i < points_no:
            distance = points.loc[i]["distance"]
            pt1 = points.iloc[[i - 1]]
            pt1x, pt1y = pt1.centroid.x, pt1.centroid.y

            if i == points_no - 1:
                pt2 = points.iloc[[i]]
            else:
                pt2 = points.iloc[[i + 1]]
            pt2x, pt2y = pt2.centroid.x, pt2.centroid.y

            pt_mid = points.iloc[[i]]
            pt_mid_x, pt_mid_y = pt_mid.centroid.x, pt_mid.centroid.y

            if i == 0:
                angle = get_angle(
                    float(pt_mid_x), float(pt_mid_y), float(pt2x), float(pt2y)
                )
            else:
                angle = get_angle(float(pt1x), float(pt1y), float(pt2x), float(pt2y))

            start = get_point(pt_mid_x, pt_mid_y, angle, -transect_length / 2)
            end = get_point(start.centroid.x, start.centroid.y, angle, transect_length)

            transects_tmp = pd.concat(
                [
                    transects_tmp,
                    pd.DataFrame(
                        {
                            "distance": [distance],
                            "id": [i],
                            "geometry": LineString([start, end]),
                        }
                    ),
                ],
                ignore_index=True,
            )
            i += 1

        transects = gpd.GeoDataFrame(
            transects_tmp, crs=transects_layer["crs"], geometry="geometry"
        )
        transects.to_file(db, layer=transects_layer["name"], driver="GPKG")
    except Exception as e:
        print("... generate_transects function error")
        raise e


def line_to_points(db, line_layer_name, points_layer_name, points_layer_crs, step):
    line_layer = fiona.open(db, layer=line_layer_name)
    line = list(line_layer)[0]
    line_layer.close()

    geometry = shape(line["geometry"])
    schema = {
        "geometry": "Point",
        "properties": {"id": "int", "distance": "float:13.2"},
    }
    with fiona.open(
        db,
        "w",
        layer=points_layer_name,
        driver="GPKG",
        schema=schema,
        OVERWRITE=1,
        crs=points_layer_crs,
    ) as output:
        for i, distance in enumerate(range(0, int(geometry.length), step)):
            point = geometry.interpolate(distance)
            output.write(
                {
                    "geometry": mapping(point),
                    "properties": {"id": i, "distance": distance},
                }
            )
        output.close()
    return i + 1 # geometry.length / step


def get_angle(pt1x, pt1y, pt2x, pt2y):
    return math.degrees(math.atan2(pt2y - pt1y, pt2x - pt1x))


def get_point(pt1x, pt1y, bearing, dist):
    bearing = math.radians(bearing + 90)
    return Point(pt1x + dist * math.cos(bearing), pt1y + dist * math.sin(bearing))
