import time
import math
import datetime

# Constants
secsInWeek = 604800
secsInDay = 86400
gpsEpoch = (1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)
gpsEpoch_as_dt = datetime.datetime(1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)
utcEpoch_as_dt = datetime.datetime(1970, 1, 1, 0, 0, 0)  # (year, month, day, hh, mm, ss)
leapsecs = 14  # NOTE: You will want to find a different way to find current leap seconds. The leapseconds module provides a good solution for this.

def utc_to_gps_for_SoW(year, month, day, hour, minute, SoW, leap_secs):
    """
    Returns the las GPS seconds for a particular SoW value.

    :param year Int year of flight including century
    :param month Int month of flight
    :param day Int day of month of flight
    :param hour Hour of flight - set to 0
    :param minute Minute of flight - set to 0
    :param SoW Seconds of week value
    :param leap_secs Leap seconds at time of flight - has been hardcoded at start of script!
    :returns las_gps_seconds for that SoW - handy for use in dataframes

    USAGE:
    lever_arms_pd['Time'] = lever_arms_pd.apply(lambda x: utc_to_gps_for_SoW(2021, 12, 2, 0, 0, x.SoWTime, 14), axis=1)
    """
    # todo compress this duplication of code.
    year = int(year)
    month = int(month)
    day = int(day)
    epoch_Tuple = gpsEpoch + (-1, -1, 0)
    t0 = time.mktime(epoch_Tuple)
    t = time.mktime((year, month, day, hour, minute, 0, -1, -1, 0))
    t = t + leap_secs
    t_diff = t - t0
    gps_week = int(math.floor(t_diff / secsInWeek))
    gps_day = int(math.floor(SoW / secsInDay))
    las_gps_secs = (SoW + (gps_week * secsInWeek)) - 1000000000
    return las_gps_secs