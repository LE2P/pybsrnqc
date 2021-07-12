"""
Module that open the data  as we want
"""

# Required Imports
import pandas as pd
import json
import os

from pyqcbsrn import utils

# -----------------------------------------------------------------------------------------------------------------

# Get data conf from JSON file
with open('./conf/autoqc_conf.json', 'r') as f:
    loaded_json = json.load(f)


class Conf:
    """
    BSRN station, database and headers from input file configurations
    """
    LAT = loaded_json['station']['LAT']
    LON = loaded_json['station']['LON']
    ALT = loaded_json['station']['ALT']
    TZ = loaded_json['station']['TZ']
    TIMESTAMP_NAME = loaded_json['header']['TIMESTAMP_NAME']
    GSW_NAME = loaded_json['header']['GSW_NAME']
    DIF_NAME = loaded_json['header']['DIF_NAME']
    DIR_NAME = loaded_json['header']['DIR_NAME']
    LWDN_NAME = loaded_json['header']['LWDN_NAME']
    TA_NAME = loaded_json['header']['TA_NAME']


# Récupération de toutes les données


def open_all(path='./dataset/', period=None, select_day=False, select_zenith=True):

    """ Open as a dataframe the brut data in a repository
    select_day = True means it doesn't take night hours
    select_zenith = True means it computes the SZA in the dataframe
    You have to choose the period of month you want """

    if period is None:

        dirs = os.listdir(path)
        dirs.remove('.keep')

    else:

        month = period[0]
        list_month = [month]

        while month != period[1]:

            if month[4:] != '12':

                month_new = str(int(month) + 1)
            else:

                year = month[:4]
                year_new = str(int(year) + 1)
                month_new = year_new + '01'

            month = month_new
            list_month.append(month)

        dirs = []

        for el in list_month:

            dirs.append(str(el) + '_brut.csv')

    print(f'Nombre de mois : {len(dirs)}')

    les_df = []

    for i in range(len(dirs)):
        df = pd.read_csv(path + dirs[i], encoding='latin-1', sep=',')
        les_df.append(df)

    fusion_df = pd.concat(les_df)

    df_fus = fusion_df.copy()

    # Zenith computation

    timestamp_list = df_fus.timestamp.to_list()
    zenith_serie = utils.getZenith(timestamp_list, Conf.LAT, Conf.LON, Conf.ALT)
    df_fus['SZA'] = list(zenith_serie)

    if select_zenith:
        # Zenith selection between 0° and 90°
        df_fus = df_fus.loc[(df_fus['SZA'] >= 0) & (df_fus['SZA'] <= 90)]

    if select_day:
        # Days selection only
        df_fus = df_fus.set_index('timestamp')
        df_fus.index = pd.to_datetime(df_fus.index)
        df_fus = df_fus.between_time('05:00:00', '19:05:00')

    df_fus = df_fus.dropna()

    return df_fus
