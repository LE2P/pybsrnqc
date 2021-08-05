#!/usr/bin/env python3
import pandas as pd
import pvlib


def isfloat(value):
    """Checking if a string can be converted to float"""
    try:
        float(value)
        return True
    except ValueError:
        return False


def getZenith(timestamp_list, lat, lon, alt):
    """From list of timestamp, return a pandas serie that associates time with its zenith angle"""
    # get local time from timestamp row with pandas approach
    date_time_utc = pd.to_datetime(timestamp_list)
    # get Solar Zenith Angle
    pv = pvlib.solarposition.get_solarposition(date_time_utc, lat, lon, alt, pressure=None, method='nrel_numpy')
    return pv.zenith
