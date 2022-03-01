import os
import pandas as pd
import struct
import time
import math
import datetime
import secsOfWeekToLASTime

def read_trjsep(proc_method, prefix_files_dic, week_orrun_flag, day_orrun_flag, day_is, m, y):
    """
    FWD/REV SEPARATION
    Reads the trjsep_ binary file and outputs a pandas dataframe with the columns 'Time',
    'Sep (nth)', 'Sep (east)', and 'Sep (down)'. Time is converted from Seconds of Week to
    adjusted GPS time.
    Sometimes, the gnss_pp_nav_sep file needs to be accessed instead; I have not ascertained why and
    Applanix have not been forthcoming with an answer, saying it is proprietary information.
    Currently the tool is set up to try using the gnss_pp first rather than fumbling around with
    the trjsep, which occasionally also has no size. A bizarre thing.

    :param prefix_files_dic: Dictionary containing full paths to relevant files.
    :param week_orrun_flag: Boolean flag indicating presence or absence of GPS week overrun.
    :param day_orrun_flag: Boolean flag indicating presence or absence of GPS day overrun.
    :param day_is: Integer representing the day of the month.
    :param y: Integer representing the year including century.
    :param m: Integer representing the month.
    :param proc_method: String representing the processing methodology. Just used to flesh out the
                        table when things go wrong.
    :return: A pandas dataframe in GPS adjusted time.

    USAGE:
    sep_pd = read_trjsep('RTX', prefix_files_dic, False, False, 27, 11, 2021)
    """
    out_file = prefix_files_dic['trjsep']
    if os.path.getsize(out_file) > 0:
        with open(out_file, 'rb') as out_f:
            d = out_f.read()
            len_no = int(len(d) / 8)
            d_code = '%sd' % len_no
            d_end_ind = int(8 * len_no)
            i_list = []
            t = struct.unpack(d_code, d[0:d_end_ind])
            for i, e in enumerate(t):
                if len(str(e)) == 18:
                    i_list.append(i)
            n = 5
            s = [t[i:i + n] for i in range(0, len(t), n)]
            if week_orrun_flag or day_orrun_flag:
                day_is = day_is - 1
            trjsep_pd = pd.DataFrame(data=s, columns=['SoWTime', 'Sep (nth)', 'Sep (east)', 'Sep (down)', 'other'])
            trjsep_pd['Time'] = trjsep_pd.apply(lambda x: utc_to_gps_for_SoW(y, m, day_is, 0, 0, x.SoWTime, leapsecs),
                                                axis=1)
            trjsep_pd = trjsep_pd[['Time', 'Sep (nth)', 'Sep (east)', 'Sep (down)', 'other']]
    else:
        ps = pd.Series(data={'Time': 'n/a', 'Sep (nth)': 'n/a', 'Sep (east)': 'n/a', 'Sep (down)': 'n/a',
                             'other': 'n/a'}, name=proc_method)
        trjsep_pd = pd.DataFrame(ps).T
    return trjsep_pd
    
def read_gnss_pp_nav_sep(prefix_files_dic, week_orrun_flag, day_orrun_flag, day_is, m, y):
    """
    FWD/REV SEPARATION
    Reads the GNSS_PP binary file and outputs a pandas dataframe with the columns 'Time',
    'Sep (nth)', 'Sep (east)', and 'Sep (down)'. Time is converted from Seconds of Week to
    adjusted GPS time.
    Sometimes, the trjsep_ file needs to be accessed instead; I have not ascertained why and
    Applanix have not been forthcoming with an answer, saying it is proprietary information.

    :param prefix_files_dic: Dictionary containing full paths to relevant files.
    :param week_orrun_flag: Boolean flag indicating presence or absence of GPS week overrun.
    :param day_orrun_flag: Boolean flag indicating presence or absence of GPS day overrun.
    :param day_is: Integer representing the day of the month.
    :param y: Integer representing the year including century.
    :param m: Integer representing the month.
    :return: A pandas dataframe in GPS adjusted time.

    USAGE:
    sep_pd = read_gnss_pp_nav_sep(prefix_files_dic, False, False, 27, 11, 2021)
    """
    out_file = prefix_files_dic['gnss_pp_nav_sep_']
    with open(out_file, 'rb') as out_f:
        d = out_f.read()
        len_no = int(len(d) / 8)
        d_code = '%sd' % len_no
        d_end_ind = int(8 * len_no)
        i_list = []
        t = struct.unpack(d_code, d[0:d_end_ind])
        for i, e in enumerate(t):
            if len(str(e)) == 18:
                i_list.append(i)
        n = 4
        s = [t[i:i + n] for i in range(0, len(t), n)]
        if week_orrun_flag or day_orrun_flag:
            day_is = day_is - 1
        gnss_pp_pd = pd.DataFrame(data=s, columns=['SoWTime', 'Sep (nth)', 'Sep (east)', 'Sep (down)'])
        gnss_pp_pd['Time'] = gnss_pp_pd.apply(lambda x: utc_to_gps_for_SoW(y, m, day_is, 0, 0, x.SoWTime, leapsecs),
                                              axis=1)
        gnss_pp_pd = gnss_pp_pd[['Time', 'Sep (nth)', 'Sep (east)', 'Sep (down)']]
        return gnss_pp_pd
    
