import os
import pandas as pd
import struct
import time
import math
import datetime
import secsOfWeekToLASTime

def read_iinkaru(prefix_files_dic, week_orrun_flag, day_orrun_flag, day_is, m, y):
    """
    SATELLITE INFORMATION.
    Reads the iinkaru_ (NOT iinkar_!!) PosPac binary file and outputs a pandas dataframe with columns
    'Time', 'Number of GPS Satellites', 'Number of Glonass Satellites', 'Number of QZSS Satellites',
    'Number of BEIDOU Satellites', 'Unknown', 'PDOP', 'Baseline Length', and 'Processing Mode'. Also
    adjusts the time from the native Seconds of Week to adjusted GPS time.
    :param prefix_files_dic: Dictionary containing full paths to relevant files.
    :param week_orrun_flag: Boolean flag indicating presence or absence of GPS week overrun.
    :param day_orrun_flag: Boolean flag indicating presence or absence of GPS day overrun.
    :param day_is: Integer representing the day of the month.
    :param y: Integer representing the year including century.
    :param m: Integer representing the month.
    :return: A pandas dataframe in GPS adjusted time.

    USAGE:
    lever_arm_pd = read_iinkaru(prefix_files_dic, False, False, 27, 11, 2021)
    """
    out_file = prefix_files_dic['iinkaru']
    with open(out_file, 'rb') as out_f:
        d = out_f.read()
        len_no = int(len(d) / 8)
        d_code = '%sd' % len_no
        d_end_ind = int(8 * len_no)
        i_list = []
        t = struct.unpack(d_code, d[0:d_end_ind])
        for i, e in enumerate(t):
            if len(str(e)) == 8:
                i_list.append(i)
        n = 9
        s = [t[i:i + n] for i in range(0, len(t), n)]
        if week_orrun_flag or day_orrun_flag:
            day_is = day_is - 1

        iinkaru_pd = pd.DataFrame(data=s,
                                  columns=['SoWTime', 'Number of GPS Satellites', 'Number of Glonass Satellites',
                                           'Number of QZSS Satellites', 'Number of BEIDOU Satellites', 'Unknown',
                                           'PDOP',
                                           'Baseline Length', 'Processing Mode'])
        iinkaru_pd['Time'] = iinkaru_pd.apply(lambda x: secsOfWeekToLASTime(y, m, day_is, 0, 0, x.SoWTime, leapsecs),
                                              axis=1)
        iinkaru_pd = iinkaru_pd[['Time', 'Number of GPS Satellites', 'Number of Glonass Satellites',
                                 'Number of QZSS Satellites', 'Number of BEIDOU Satellites', 'Unknown', 'PDOP',
                                 'Baseline Length', 'Processing Mode']]
        return iinkaru_pd