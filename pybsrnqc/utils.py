#!/usr/bin/env python3
import cassandra
import sys
import os
import re
import pandas as pd
import pvlib
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import date, datetime, timedelta
from pytz import timezone

class bcolors:
    """Colors"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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


def decryption(loaded_json):
    """Symmetric encryption, we use the Fernet class which is an implementation of AES"""
    license = loaded_json['cassandra']['license']
    password = license.encode()
    salt = b'SWIO-Energy'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    decrypted = f.decrypt(bytes(loaded_json['cassandra']['keyspace'], 'utf-8'))
    return decrypted.decode("utf-8")


def raiseError(loaded_json, cluster, ncfile, exception, msgErr):
    """when an error is raised : close properly the cluster and ncfile, print error message and quit the program"""
    if exception:
        print(bcolors.HEADER+'Caught this exception: '+repr(exception)+bcolors.ENDC)
    elif msgErr:
        print(bcolors.FAIL+"ERROR!"+bcolors.ENDC)
        print(bcolors.FAIL+msgErr+bcolors.ENDC)
    # Catch error
    listError = ['NoHostAvailable', 'KeyError', 'ValueError', 'IndexError']
    if str(exception.__class__.__name__) in listError:
        print(bcolors.FAIL+msgErr+""+bcolors.ENDC)
    # Close properly
    if ncfile:
        # remove text file
        DATA_PATH = loaded_json['path']['DATA_PATH']
        DATA_CSV_PATH = loaded_json['path']['DATA_CSV_PATH']
        csvFilePath = remove_prefix(ncfile.filepath(), DATA_PATH)
        if csvFilePath is not False:
            csvFilePath = re.sub(r'.nc', '.csv', DATA_CSV_PATH+csvFilePath)
            os.system('rm '+csvFilePath)
            print("Remove csv file: \""+csvFilePath)
        # remove NetCDF file
        os.system('rm '+ncfile.filepath())
        print("Remove NetCDF file: \""+ncfile.filepath())
        ncfile.close()

    if cluster:
        cluster.shutdown()  # print "cassandra connection is closed!"
    # exit the program
    sys.exit('errorIsRaised')


def getStationName(session, transaction_id):
    """get name of the station from the id transaction"""
    rows = session.execute("SELECT name FROM transaction WHERE transaction_id="+str(transaction_id))
    for transaction in rows:
        return transaction.name


def getMetaTrans(session, transaction_id):
    """get metadata from the meta_search table link to the transaction"""
    # Init variables
    key, value = [], []
    # We add the station name and the transaction_id to the dictionnary
    station_name = getStationName(session, transaction_id)
    key = ['transaction_id', 'station_name']
    value = [transaction_id, station_name]
    # Make dictionnary of metadata
    rows = session.execute("SELECT * FROM meta_search WHERE transaction_id="+str(transaction_id)+" LIMIT 2")
    for meta_search in rows:
        for meta_list in meta_search:
            if isinstance(meta_list, cassandra.util.OrderedMapSerializedKey):
                for meta_name in meta_list:
                    if "locality" in meta_name:
                        short_meta_name = re.sub(r'.*locality_', '', meta_name)  # get only the useful string
                        key.append(short_meta_name)
                        value.append(meta_list[meta_name])
                    if "system" in meta_name:
                        short_meta_name = re.sub(r'.*system_', '', meta_name)
                        key.append(short_meta_name)
                        value.append(meta_list[meta_name])
                    if "CFConventions" in meta_name:
                        short_meta_name = re.sub(r'.*CFConventions_', '', meta_name)
                        key.append(short_meta_name)
                        value.append(meta_list[meta_name])
    metaTransDictionary = dict(zip(key, value))
    return metaTransDictionary


def getSensorDataUTC(session, transaction_id, sensor_id, startDay, endDay, timeList, valueList):
    """get all values and dates from the sensor and return both list"""
    # We extract the year from the date
    startDay_date = datetime.strptime(startDay, '%Y-%m-%d %H:%M:%S')
    endDay_date = datetime.strptime(endDay, '%Y-%m-%d %H:%M:%S')
    year = startDay_date.year
    tamp = startDay_date
    # Make the request
    rows = session.execute("SELECT date, sensor_id, value FROM sensor_data WHERE transaction_id="+str(transaction_id)+" \
    AND sensor_id='"+sensor_id+"' AND year="+str(year)+" AND date>='"+startDay+"' AND date<='"+endDay+"'")
    # Get the last date of data available in the database
    lastSensorDate = rows[-1].date
    # Create data list
    for sensor_data in rows:
        # Test for blank value
        if sensor_data.date != tamp:
            while sensor_data.date > tamp:
                timeList.append(tamp.astimezone(timezone('Indian/Reunion')))  # ajust timezone to get UTC
                valueList.append(None)
                tamp = tamp + timedelta(minutes=1)
        timeList.append((sensor_data.date).astimezone(timezone('Indian/Reunion')))  # ajust timezone to get UTC
        valueList.append(sensor_data.value)
        # Fix buffer variable
        tamp = tamp + timedelta(minutes=1)
        # Fix None value for no dataArray
        if sensor_data.date == lastSensorDate:
            while endDay_date >= tamp:
                timeList.append(tamp.astimezone(timezone('Indian/Reunion')))  # ajust timezone to get UTC
                valueList.append(None)
                tamp = tamp + timedelta(minutes=1)
        if tamp == endDay_date + timedelta(minutes=1):
            tamp = startDay_date
    tamp = startDay_date
    return timeList, valueList