import pandas as pd
import numpy as np


def get_profile_section_len(profile):
    return round(
        (
            (profile.x_geo[1] - profile.x_geo[0]) ** 2
            + (profile.y_geo[1] - profile.y_geo[0]) ** 2
        )
        ** (0.5),
        3,
    )


def set_status(result, status):
    result["status"] = status


def get_zero_points(profile, begin_no, end_no, elevation_zero, min_profile_points=20):
    retVal = {"first": None, "last": None, "status": "OK"}

    # section_len = get_profile_section_len(profile)
    if (
        begin_no < end_no
        and len(profile) >= end_no
        and end_no - begin_no >= min_profile_points
    ):
        # any zero or lower values?
        _profile = profile.iloc[begin_no:end_no]
        if (_profile["elevation"] <= elevation_zero).any():
            retVal["first"] = _profile[_profile["elevation"] > elevation_zero].index[0]
            retVal["last"] = (
                _profile[_profile["elevation"] <= elevation_zero].index[-1] + 1
            )
        else:
            retVal["first"] = begin_no
            retVal["last"] = begin_no
    else:
        set_status(
            retVal,
            f"Minimal transet length = {min_profile_points} ({begin_no}:{end_no})",
        )
    return retVal


def method_2(profile, begin_no, end_no, min_profile_points=20):
    retVal = {"top": None, "bottom": None, "status": "OK"}

    section_len = get_profile_section_len(profile)
    if (
        begin_no < end_no
        and len(profile) >= end_no
        and end_no - begin_no >= min_profile_points
    ):
        # a = (he - hb) / (de - db)
        a = (profile.elevation[end_no] - profile.elevation[begin_no]) / (
            end_no * section_len - begin_no * section_len
        )
        # b = hb - (he - hb) / (de - db) * db
        b = (
            profile.elevation[begin_no]
            - (profile.elevation[end_no] - profile.elevation[begin_no])
            / (end_no * section_len - begin_no * section_len)
            * begin_no
            * section_len
        )

        D = []
        for idx in range(begin_no, end_no + 1):
            # Di = (-a * di + h1 - b) / (a**2 + 1)**(0.5)
            D.append(
                ((-a) * idx * section_len + profile.elevation[idx] - b)
                / (a**2 + 1) ** (0.5)
            )

        D_min_index = np.array(D).argmin()
        retVal["bottom"] = begin_no + D_min_index
        D_max_index = np.array(D[D_min_index:]).argmax() + D_min_index
        retVal["top"] = begin_no + D_max_index
    else:
        set_status(
            retVal,
            f"Minimal transet length = {min_profile_points} ({begin_no}:{end_no})",
        )

    return retVal
