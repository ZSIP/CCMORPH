from scipy.signal import savgol_filter
import pandas as pd

def smooth_profile(profile, begin_no, end_no, window=9, degree=3):
    # Savitzky-Golay Filter
    try:
        return savgol_filter(profile.elevation[begin_no:end_no], window, degree)
    except:
        return None

def smooth_points(points):
    try:
        return points.mask(points.sub(points.mean()).div(points.std()).abs().gt(1))
        # return points.mask(points.sub(points.mean()).div(points.std()).abs().gt(1)).interpolate()
    except:
        return None