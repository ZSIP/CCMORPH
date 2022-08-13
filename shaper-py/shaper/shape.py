import math
import pandas as pd

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

        D_min = min(D)
        D_max = max(D)
        retVal["top"] = begin_no + D.index(D_max)
        retVal["bottom"] = begin_no + D.index(D_min)
    else:
        set_status(
            retVal,
            f"Minimal transet length = {min_profile_points} ({begin_no}:{end_no})",
        )

    return retVal


def method_1(profile, begin_no, end_no, min_profile_points=20, elevation_threshold=3, profile_id=0, debug=False):
    retVal = {"top": None, "bottom": None, "status": "OK", "debug": None}
    debug_info = pd.DataFrame({"elevation": profile.elevation})

    section_len = get_profile_section_len(profile)
    if (
        begin_no < end_no
        and len(profile) >= end_no
        and end_no - begin_no >= min_profile_points
    ):
        H1 = profile.elevation.diff() / section_len

        debug_info["H1"] = H1

        H2 = H1.shift(-1).diff() / section_len # shift +1
        debug_info["H2"] = H2

        k = H2 / ((1 + H1 ** 2) ** (1.5))

        debug_info["k"] = k

        begin = begin_no if begin_no > 0 else 1
        end = end_no if end_no < len(H2) - 1 else len(H2) - 2
        k_min_idx = k[begin:end].idxmin()

        debug_info["k_min_idx"] = k_min_idx

        begin = k_min_idx - 5 if k_min_idx - 5 > begin_no else begin_no
        end = k_min_idx + 5 if k_min_idx + 5 < end_no else end_no
        h_local_max_idx = profile.elevation[begin:end].idxmax()

        debug_info["h_local_max_idx"] = h_local_max_idx

        h_local_max_idx = k_min_idx if h_local_max_idx == end - 1 else h_local_max_idx # !!!
        h_local_max = profile.elevation[h_local_max_idx]        
        D_high = None if h_local_max < elevation_threshold else h_local_max

        debug_info["elevation_threshold"] = elevation_threshold

        D_low_idx = None

        if D_high:
            D_high_idx = h_local_max_idx
            retVal["top"] = D_high_idx

            if D_high_idx > 0:
                # begin? end?
                e_th = profile.loc[profile['elevation'] > elevation_threshold]
                e_0 = profile.loc[profile['elevation'] >= 0]
                if e_th.iloc[0].no_point - e_0.iloc[0].no_point <= 0:
                    set_status(retVal, 'invalid elevation threshold')
                    return retVal
                k_low_max_idx = H2_local_max_idx = H2[e_0.iloc[0].no_point:e_th.iloc[0].no_point].idxmax()

                debug_info["H2_local_max_idx"] = H2_local_max_idx


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

    if debug:
        retVal['debug'] = debug_info

    return retVal
