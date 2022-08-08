from scipy.signal import savgol_filter


def smooth_profile(profile, begin_no, end_no, window=9, degree=3):

    try:
        return savgol_filter(profile.elevation[begin_no:end_no], window, degree)
    except:
        return None
