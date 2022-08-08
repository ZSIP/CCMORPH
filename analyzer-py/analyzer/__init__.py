from analyzer.smooth import smooth_profile

from analyzer.measure import get_points_by_elevation
from analyzer.measure import get_distance
from analyzer.measure import get_slope
from analyzer.measure import get_volume

from analyzer.analyze import method_1, method_2


def get_main_points(
    profile,
    begin_no,
    end_no,
    method=1,
    min_profile_points=20,
    elevation_threshold=3,
    profile_id=0,
    debug=False,
):
    retVal = None
    if method == 1:
        retVal = method_1(
            profile,
            begin_no,
            end_no,
            min_profile_points=min_profile_points,
            elevation_threshold=elevation_threshold,
            profile_id=profile_id,
            debug=debug,            
        )
    elif method == 2:
        retVal = method_2(
            profile,
            begin_no,
            end_no,
            min_profile_points=min_profile_points,
        )
    return retVal