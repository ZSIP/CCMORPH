import math
import numpy as np

RAD_2_DEG = 360 / (2 * math.pi)

def get_points_by_elevation(elevations, profile, begin_no, end_no):
    result = []
    if begin_no < end_no and len(profile) >= end_no and len(elevations) > 0:
        # elevations eg. [0, 1]
        # returns { 0: [no1, no2, ...], 1: [no3, no5, ...]}]
        result = {}
        for e in elevations:
            result[e] = []

        for idx in range(begin_no, end_no):
            current = profile.elevation[idx]
            next = profile.elevation[idx + 1]
            for e in elevations:
                if (current - e) * (next - e) <= 0:
                    point = idx if abs(current - e) < abs(next - e) else idx + 1
                    # print(f'--- {idx} {e} {current["elevation"]} {next["elevation"]}')
                    result[e].append(point)
    return result

def get_surface_under(profile, begin_no, end_no, is_absolute):
    # returns m2
    result = 0
    if begin_no < end_no and len(profile) >= end_no:
        distance = math.sqrt(math.pow(profile.x_geo[begin_no + 1] - profile.x_geo[begin_no], 2) + math.pow(profile.y_geo[begin_no + 1] - profile.y_geo[begin_no], 2))
        for idx in range(begin_no, end_no):
            tmp = ((profile.elevation[idx] + profile.elevation[idx + 1]) if is_absolute else (profile.elevation[idx + 1]) - (profile.elevation[idx]) * distance) / 2
            result += tmp if tmp > 0 else 0
    return result

def get_distance(profile, begin_no, end_no):
    # returns m
    result = None
    if begin_no < end_no and len(profile) >= end_no:
        result =  math.sqrt(math.pow(profile.x_geo[end_no] - profile.x_geo[begin_no], 2) + math.pow(profile.y_geo[end_no] - profile.y_geo[begin_no], 2))
    return result

def get_slope(profile, begin_no, end_no):
    # returns degrees
    result = None
    if begin_no < end_no and len(profile) >= end_no:
        distance = get_distance(profile, begin_no, end_no)
        slope = (profile.elevation[end_no] - profile.elevation[begin_no]) / distance
        result = math.degrees(math.atan(slope))
    return result

def get_volume(width, profile, begin_no, end_no, is_absolute):
    # returns m3 
    return width * get_surface_under(profile, begin_no, end_no, is_absolute)
