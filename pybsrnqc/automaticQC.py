#!/usr/bin/env python3
import csv
import datetime
import os
from collections import OrderedDict
from pathlib import Path

import pandas as pd
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.plotting import figure, output_file, show

from pybsrnqc.config import Station, Coef, Header
from pybsrnqc.qcrad import QC1, QC2, QC3, QC5, QC7, QC8, QC10, QC19
from pybsrnqc.utils import isfloat, getZenith

default_station = Station()
default_coef = Coef()
default_header = Header()


def fix_values(row: OrderedDict, header: Header = default_header):
    GSW, Dif, DirN, LWdn, Ta, Td = None, None, None, None, None, None
    # check variables name on input file
    try:
        timestamp = row[header.TIMESTAMP_NAME]
        if header.GSW_NAME in row and isfloat(row[header.GSW_NAME]):
            GSW = float(row[header.GSW_NAME])
        if header.DIF_NAME in row and isfloat(row[header.DIF_NAME]):
            Dif = float(row[header.DIF_NAME])
        if header.DIR_NAME in row and isfloat(row[header.DIR_NAME]):
            DirN = float(row[header.DIR_NAME])
        if header.LWDN_NAME in row and isfloat(row[header.LWDN_NAME]):
            LWdn = float(row[header.LWDN_NAME])
        if header.TA_NAME in row and isfloat(row[header.TA_NAME]):
            Ta = float(row[header.TA_NAME]) + 273.15
    except KeyError as e:
        print('KeyError: %s' % str(e))
    except ValueError as valueError:
        print('ValueError: %s' % str(valueError))
    return timestamp, GSW, Dif, DirN, LWdn, Ta


def getRow(row: OrderedDict, zenith_serie, coef: Coef = default_coef, header: Header = default_header):
    # get values of parameters
    [timestamp, GSW, Dif, DirN, LWdn, Ta] = fix_values(row, header)
    SZA = float(zenith_serie[timestamp])
    # application of data quality control
    qc_result = {
        "timestamp": timestamp,
        "QC1": QC1(GSW, SZA, coef),
        "QC2": QC2(Dif, SZA, coef),
        "QC3": QC3(DirN, SZA, coef),
        "QC5": QC5(LWdn, coef),
        "QC7": QC7(GSW, Dif, DirN, SZA),
        "QC8": QC8(Dif, GSW, SZA),
        "QC10": QC10(LWdn, Ta, coef),
        "QC19": QC19(Ta)
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


def generateQCFiles(filepath, station: Station = default_station, coef: Coef = default_coef):
    """Create the 2 files _aqc.csv and _qrcad.csv"""
    print(filepath)
    # Manage filenames
    FILE_BRUT = filepath
    FILE_AQC = os.path.splitext(FILE_BRUT.replace('_brut', ''))[0] + '_aqc.csv'
    FILE_QCRAD = os.path.splitext(FILE_BRUT.replace('_brut', ''))[0] + '_qcrad.csv'
    # load input file into a DataFrame
    file_brut = pd.read_csv(FILE_BRUT)
    timestamp_list = file_brut.timestamp.to_list()
    zenith_serie = getZenith(timestamp_list, station.LAT, station.LON, station.ALT)
    # process input file
    datapoints_qcrad, datapoints_aqc = [], []
    with open(FILE_BRUT, 'r') as fileIn:
        reader = csv.DictReader(fileIn, delimiter=',')
        for row in reader:
            (row_aqc, row_qcrad) = getRow(row, zenith_serie, coef)
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
