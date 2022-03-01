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

def read_iincal(prefix_files_dic, week_orrun_flag, day_orrun_flag, day_is, y, m):
    """
    LEVER ARM DETERMINATION.
    Reads the iincal_ pospac binary file and returns a pandas dataframe with columns 'Time', 'X',
    'Y', and 'Z', where Time is in adjusted GPS seconds and X, Y, and Z are the lever arm values
    in metres. It also checks one last time for any GPS week overruns and updates the week overrun
    flag if necessary.
    :param prefix_files_dic: Dictionary containing all "relevant" ephemeris files. The relevant file
           has key 'iincal'.
    :param week_orrun_flag: Boolean flag for detection of any GPS week overrun.
    :param day_orrun_flag:  Boolean flag for detection of any GPS day overrun.
    :param day_is: Integer representing the day of the month.
    :param y: Integer representing the year including century.
    :param m: Integer representing the month.
    :return: Pandas dataframe as mentioned above, plus the potentially updated week overrun flag.

    USAGE:
    lever_arm_pd, week_orrun_flag = read_iincal(prefix_files_dic, False, False, 27, 2021, 11)
    """
    out_file = prefix_files_dic['iincal']
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
        n = 29  # 29  33
        print('iincal start')  # handy when you are keeping an eye on where a timing issue is coming in
        print(t[0])
        s = [t[i:i + n] for i in range(0, len(t), n)]
        # test n is correct
        end_list = [b[-1] for b in s if float(b[-1]) != 0.0]
        if len(end_list) > 0:
            # I have found occasions where the line length changes abruptly mid-file.
            # This is rare these days, but this is here to catch that.
            logging.info('switching line splitter')  # If it reports it, maybe one day I will work out the pattern...
            n = 33
            s = [t[i:i + n] for i in range(0, len(t), n)]
        # This section does the sanity check for week overruns. It could probably be put into
        # a separate function one day.
        sows = []
        for p, record in enumerate(s):
            SoW = record[0]
            sows.append(SoW)
        if sows[-1] > 604800 or sows[-1] == 0:
            week_orrun_flag = True
        # This line is repeated in each binary read. It's tempting to make the day change permanent,
        # but this turned out to be a Bad Idea. Don't repeat my mistake.
        # (I don't remember what happened exactly, but it wasn't good.)
        if week_orrun_flag or day_orrun_flag:
            day_is = day_is - 1
        # finally, dataframe time
        iin_cal_df = pd.DataFrame(data=s)
        iin_cal_df = iin_cal_df.iloc[:, :4]
        iin_cal_df.columns = ['SoWTime', 'X', 'Y', 'Z']
        # convert Seconds of Week time in the file to Adjusted GPS time
        iin_cal_df['Time'] = iin_cal_df.apply(lambda x: secsOfWeekToLASTime(y, m, day_is, 0, 0, x.SoWTime, leapsecs),
                                              axis=1)
        iin_cal_df = iin_cal_df[['Time', 'X', 'Y', 'Z']]
        return iin_cal_df, week_orrun_flag