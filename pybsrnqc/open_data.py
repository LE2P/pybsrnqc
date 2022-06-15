"""
Module that open the data  as we want
"""

import os

import pandas as pd

from pybsrnqc.config import Station
from pybsrnqc.utils import getZenith


# -----------------------------------------------------------------------------------------------------------------

# Récupération de toutes les données


def open_all(path='./dataset', period=None, select_day=False, select_zenith=True, station: Station = Station()):
    """ Open as a dataframe the brut data in a repository
    select_day = True means it doesn't take night hours
    select_zenith = True means it computes the SZA in the dataframe
    You have to choose the period of month you want """
    path = path + '/'
    if period is None:

        dirs = os.listdir(path)
        if '.keep' in dirs:
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
    zenith_serie = getZenith(timestamp_list, station.LAT, station.LON, station.ALT)
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
