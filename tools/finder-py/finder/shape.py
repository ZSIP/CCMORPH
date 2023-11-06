import math
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

    section_len = get_profile_section_len(profile)
    if (
        begin_no < end_no
        and len(profile) >= end_no
        and end_no - begin_no >= min_profile_points
    ):
        # any zero or lower values?
        _profile = profile.iloc[begin_no:end_no]
        if (_profile['elevation'] <= elevation_zero).any():
            retVal['first'] = _profile[_profile['elevation'] > elevation_zero].index[0]
            retVal['last'] = _profile[_profile['elevation'] <= elevation_zero].index[-1] + 1
        else:
            retVal['first'] = begin_no
            retVal['last'] = begin_no
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
                / (a ** 2 + 1) ** (0.5)
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


def method_1(profile, begin_no, end_no, min_profile_points=20, elevation_threshold=3, profile_id=0):
    retVal = {"top": None, "bottom": None, "status": "OK"}

    section_len = get_profile_section_len(profile)
    if (
        begin_no < end_no
        and len(profile) >= end_no
        and end_no - begin_no >= min_profile_points
    ):
        H1 = profile.elevation.diff() / section_len
        H2 = H1.shift(-1).diff() / section_len # shift +1
        k = H2 / ((1 + H1 ** 2) ** (1.5))

        begin = begin_no if begin_no > 0 else 1
        end = end_no if end_no < len(H2) - 1 else len(H2) - 2
        k_min_idx = k[begin:end].idxmin()

        begin = k_min_idx - 5 if k_min_idx - 5 > begin_no else begin_no
        end = k_min_idx + 5 if k_min_idx + 5 < end_no else end_no
        h_local_max_idx = profile.elevation[begin:end].idxmax()

        h_local_max_idx = k_min_idx if h_local_max_idx == end - 1 else h_local_max_idx # !!!
        h_local_max = profile.elevation[h_local_max_idx]        
        D_high = None if h_local_max < elevation_threshold else h_local_max

        D_low_idx = None

        if D_high:
            D_high_idx = h_local_max_idx
            retVal["top"] = D_high_idx

            if D_high_idx > 0:
                # begin? end? todo
                e_th = profile[begin_no:end_no].loc[profile['elevation'] > elevation_threshold]
                e_0 = profile[begin_no:end_no].loc[profile['elevation'] >= 0]
                if e_th.iloc[0].no_point - e_0.iloc[0].no_point <= 0:
                    set_status(retVal, 'invalid elevation threshold')
                    return retVal
                k_low_max_idx = H2_local_max_idx = H2[e_0.iloc[0].no_point:e_th.iloc[0].no_point].idxmax()

                if not math.isnan(H2_local_max_idx):
                    k_low_max_idx = k[e_0.iloc[0].no_point:e_th.iloc[0].no_point].idxmax()
                    D_low_idx = (
                        H2_local_max_idx
                        if H2_local_max_idx - 5 < k_low_max_idx < H2_local_max_idx + 5
                        else None
                    )

        if D_low_idx:
            retVal["bottom"] = D_low_idx
    else:
        set_status(
            retVal,
            f"Minimal transet length = {min_profile_points} ({begin_no}:{end_no})",
        )

    return retVal
