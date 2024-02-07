from finder.smooth import smooth_profile
from finder.smooth import smooth_points
from finder.shape import get_zero_points
from finder.shape import method_2


def get_main_points(
    profile,
    begin_no,
    end_no,
    method=2,
    min_profile_points=20,
):
    retVal = None
    if method == 2:
        retVal = method_2(
            profile,
            begin_no,
            end_no,
            min_profile_points=min_profile_points,
        )
    return retVal
