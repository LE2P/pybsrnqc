#!/usr/bin/env python3
import csv
import json
import importlib.resources
import os
import pandas as pd
import datetime
from collections import OrderedDict
from pathlib import Path
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.plotting import figure, output_file, show
from pybsrnqc import utils
from pybsrnqc import qc_functions as qcf

# Get data conf from JSON files
with importlib.resources.path("pybsrnqc", "qcrad_conf.json") as data_path:
    with open(data_path, 'r') as f:
        loaded_json = json.load(f)

# Configuration of some static variables


class conf:
    """
    BSRN station, database and headers from input file configurations
    """
    LAT = loaded_json['STATION']['LAT']
    LON = loaded_json['STATION']['LON']
    ALT = loaded_json['STATION']['ALT']
    TZ = loaded_json['STATION']['TZ']
    TIMESTAMP_NAME = loaded_json['HEADER']['TIMESTAMP_NAME']
    GSW_NAME = loaded_json['HEADER']['GSW_NAME']
    DIF_NAME = loaded_json['HEADER']['DIF_NAME']
    DIR_NAME = loaded_json['HEADER']['DIR_NAME']
    LWDN_NAME = loaded_json['HEADER']['LWDN_NAME']
    TA_NAME = loaded_json['HEADER']['TA_NAME']


def fix_values(row: OrderedDict):
    GSW, Dif, DirN, LWdn, Ta, Td = None, None, None, None, None, None
    # check variables name on input file
    try:
        timestamp = row[conf.TIMESTAMP_NAME]
        if conf.GSW_NAME in row and utils.isfloat(row[conf.GSW_NAME]):
            GSW = float(row[conf.GSW_NAME])
        if conf.DIF_NAME in row and utils.isfloat(row[conf.DIF_NAME]):
            Dif = float(row[conf.DIF_NAME])
        if conf.DIR_NAME in row and utils.isfloat(row[conf.DIR_NAME]):
            DirN = float(row[conf.DIR_NAME])
        if conf.LWDN_NAME in row and utils.isfloat(row[conf.LWDN_NAME]):
            LWdn = float(row[conf.LWDN_NAME])
        if conf.TA_NAME in row and utils.isfloat(row[conf.TA_NAME]):
            Ta = float(row[conf.TA_NAME]) + 273.15
    except KeyError as e:
        print('KeyError: %s' % str(e))
    except ValueError as valueError:
        print('ValueError: %s' % str(valueError))
    return (timestamp, GSW, Dif, DirN, LWdn, Ta)


def getRow(row: OrderedDict, zenith_serie):
    # get values of parameters
    [timestamp, GSW, Dif, DirN, LWdn, Ta] = fix_values(row)
    SZA = float(zenith_serie[timestamp])
    # application of data quality control
    qc_result = {
        "timestamp": timestamp,
        "QC1": qcf.QC1().lab(SZA, GSW, loaded_json),
        "QC2": qcf.QC2().lab(SZA, Dif, loaded_json),
        "QC3": qcf.QC3().lab(SZA, DirN, loaded_json),
        "QC5": qcf.QC5().lab(SZA, LWdn, loaded_json),
        "QC10": qcf.QC10().lab(Ta, LWdn, loaded_json),
        "QC19": qcf.QC19(Ta)
    }
    # create row for aqc file
    row_aqc = row
    for key in row_aqc.keys():
        if key != "timestamp":
            row_aqc[key] = 0
    if qc_result["QC1"] > 2:
        row_aqc["global2_avg"] = 1
        row_aqc["global2_std"] = 1
        row_aqc["global2_min"] = 1
        row_aqc["global2_max"] = 1
    if qc_result["QC2"] > 2:
        row_aqc["diffuse_avg"] = 1
        row_aqc["diffuse_std"] = 1
        row_aqc["diffuse_min"] = 1
        row_aqc["diffuse_max"] = 1
    if qc_result["QC3"] > 2:
        row_aqc["direct_avg"] = 1
        row_aqc["direct_std"] = 1
        row_aqc["direct_min"] = 1
        row_aqc["direct_max"] = 1
    if qc_result["QC5"] > 2:
        row_aqc["downward_avg"] = 1
        row_aqc["downward_std"] = 1
        row_aqc["downward_min"] = 1
        row_aqc["downward_max"] = 1
    if qc_result["QC19"] > 0:
        row_aqc["temperature"] = 1
    # create row for qcrad file
    row_qcrad = qc_result
    return row_aqc, row_qcrad


def generateQCFiles(filepath):
    """Create the 2 files _aqc.csv and _qrcad.csv"""
    print(filepath)
    # Manage filenames
    FILE_BRUT = filepath
    FILE_AQC = os.path.splitext(FILE_BRUT.replace('_brut', ''))[0] + '_aqc.csv'
    FILE_QCRAD = os.path.splitext(FILE_BRUT.replace('_brut', ''))[0] + '_qcrad.csv'
    # load input file into a DataFrame
    file_brut = pd.read_csv(FILE_BRUT)
    timestamp_list = file_brut.timestamp.to_list()
    zenith_serie = utils.getZenith(timestamp_list, conf.LAT, conf.LON, conf.ALT)
    # process input file
    datapoints_qcrad, datapoints_aqc = [], []
    with open(FILE_BRUT, 'r') as fileIn:
        reader = csv.DictReader(fileIn, delimiter=',')
        for row in reader:
            (row_aqc, row_qcrad) = getRow(row, zenith_serie)
            datapoints_qcrad.append(row_qcrad)
            datapoints_aqc.append(row_aqc)
    # convert list of qcrad results into dataframe & save as a csv file
    df_qcrad = pd.DataFrame(datapoints_qcrad)
    df_qcrad.to_csv(FILE_QCRAD, index=False)
    print("Successfully saved CSV file in", FILE_QCRAD)
    # convert list of aqc results into dataframe & save as a csv file
    df_aqc = pd.DataFrame(datapoints_aqc)
    df_aqc.to_csv(FILE_AQC, index=False)
    print("Successfully saved CSV file in", FILE_AQC)


def plotQCFiles(filepath):
    """Plot the input file"""
    # init
    csv_name = filepath
    df = pd.read_csv(filepath)
    year = df['timestamp'][0][:4]
    month = df['timestamp'][0][5:7]
    yearMonth = year + month
    typeFile = 'brut'
    # create directory if it necessary
    Path("plot/" + yearMonth).mkdir(parents=True, exist_ok=True)
    chart_name = 'plot/' + yearMonth + '/' + typeFile + '.html'
    if typeFile == "qcrad":
        parameters_to_plot = ["QC1", "QC2", "QC3", "QC5", "QC7", "QC8", "QC10", "QC19"]
    else:
        parameters_to_plot = ["global2_avg", "diffuse_avg", "direct_avg", "downward_avg", "temperature"]
    # get sensor data
    df = pd.read_csv(csv_name)
    timestamp = df.timestamp.to_list()
    date = []
    for time in timestamp:
        date.append(datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))
    df.insert(1, "date", date)
    source = ColumnDataSource(df)
    # create plots and choose color
    plots = []
    for var in parameters_to_plot:
        hover = HoverTool()
        s = figure(plot_width=1600, plot_height=900, x_axis_type="datetime")
        s.circle(x='date', y=var, source=source)
        s.line(x='date', y=var, legend_label=var, source=source)
        hover.tooltips = [
            ('date', '@date{%F %T}'),
            (var, '@' + var)
        ]
        hover.formatters = {'@date': 'datetime'}
        s.add_tools(hover)
        plots.append(s)
    # show and save plot
    output_file(chart_name)
    print("Successfully saved HTML file in", chart_name)
    show(column(plots))
