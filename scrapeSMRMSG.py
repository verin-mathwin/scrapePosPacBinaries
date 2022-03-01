import os
import pandas as pd
import struct
import time
import math
import datetime
import secsOfWeekToLASTime

# Constants
secsInWeek = 604800
secsInDay = 86400
gpsEpoch = (1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)
gpsEpoch_as_dt = datetime.datetime(1980, 1, 6, 0, 0, 0)  # (year, month, day, hh, mm, ss)
utcEpoch_as_dt = datetime.datetime(1970, 1, 1, 0, 0, 0)  # (year, month, day, hh, mm, ss)
leapsecs = 14  # NOTE: You will want to find a different way to find current leap seconds. The leapseconds module provides a good solution for this.

def read_smrmsg(prefix_files_dic, week_orrun_flag, day_orrun_flag, day_is, m, y):
    """
    Errors!
    Literally this file - the smrmsg file - holds all information about the RMSE issues you see in
    the charts. This script takes that file and converts it into a pandas datafrane in adjusted GPS.
    Can get a bit chonky in larger flights.
    :param prefix_files_dic: Dictionary containing full paths to relevant files.
    :param week_orrun_flag: Boolean flag indicating presence or absence of GPS week overrun.
    :param day_orrun_flag: Boolean flag indicating presence or absence of GPS day overrun.
    :param day_is: Integer representing the day of the month.
    :param y: Integer representing the year including century.
    :param m: Integer representing the month.
    :return: A pandas dataframe in GPS adjusted time.

    USAGE:
    smrmsg_pd = read_smrmsg(prefix_files_dic, False, False, 27, 11, 2021)
    """
    out_file = prefix_files_dic['smrmsg']
    with open(out_file, 'rb') as sample:
        d = sample.read()
        len_no = int(len(d) / 8)
        d_code = '%sd' % len_no
        d_end_ind = int(8 * len_no)
        t = struct.unpack(d_code, d[0:d_end_ind])
        n = 10
        s = [t[i:i + n] for i in range(0, len(t), n)]
        if week_orrun_flag or day_orrun_flag:
            day_is = day_is - 1
        smrmsg_pd = pd.DataFrame(s, columns=['SoWTime', 'North Position Error RMSE', 'East Position Error RMSE',
                                             'Down Position Error RMSE', 'North Velocity Error RMSE',
                                             'East Velocity Error RMSE', 'Down Velocity Error RMSE', 'Roll Error RMSE',
                                             'Pitch Error RMSE', 'Heading Error RMSE'])
        smrmsg_pd['Time (s)'] = smrmsg_pd.apply(lambda x: secsOfWeekToLASTime(y, m, day_is, 0, 0, x.SoWTime, leapsecs),
                                                axis=1)
        smrmsg_pd = smrmsg_pd[['Time (s)', 'North Position Error RMSE', 'East Position Error RMSE',
                               'Down Position Error RMSE', 'North Velocity Error RMSE',
                               'East Velocity Error RMSE', 'Down Velocity Error RMSE', 'Roll Error RMSE',
                               'Pitch Error RMSE', 'Heading Error RMSE']]

        return smrmsg_pd