#!/usr/bin/env python3
from bokeh import events
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import CustomJS, HoverTool, Panel, Tabs, Button, DateFormatter
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.palettes import Colorblind, Plasma
from bokeh.plotting import ColumnDataSource, figure, output_file, show
from os import makedirs, path
from pandas import read_csv, to_datetime

import importlib.resources


def plotBSRN(filepath: str, patterns: list[str] = None, timeStart: str = None, timeEnd: str = None):

    # Import file
    yearMonth = path.basename(filepath).split("_")[0]
    bsrnFile = read_csv(filepath)

    # Truncate data between date
    timeStartIndex = None
    timeEndIndex = None
    if timeStart is not None:
        timeStartIndex = bsrnFile.timestamp[bsrnFile.timestamp == timeStart].index[0]
    if timeEnd is not None:
        timeEndIndex = bsrnFile.timestamp[bsrnFile.timestamp == timeEnd].index[0] + 1
    bsrnFile = bsrnFile[timeStartIndex:timeEndIndex]
    bsrnFile.timestamp = to_datetime(bsrnFile.timestamp, format="%Y-%m-%d %H:%M:%S")

    # Creation column data source
    sensors = bsrnFile.columns
    if patterns is not None:
        sensors = [match for match in bsrnFile.columns if any(pattern in match for pattern in patterns)]
    varNames = sensors[:]
    varNames.insert(0, "timestamp")
    bsrnData = ColumnDataSource(data=bsrnFile[varNames])
    bsrnSelect = ColumnDataSource(data={name: [] for name in varNames})
    columns = [TableColumn(field=name) for name in varNames]
    columns[0].formatter = DateFormatter(format="%Y-%m-%d %H:%M:%S")
    tableData = DataTable(
        source=bsrnSelect, columns=columns, sizing_mode="stretch_both",
        sortable=True, selectable=True, editable=False
    )

    # Selection
    with importlib.resources.path("pybsrnqc", "callbackSelect.js") as data_path:
        f = open(data_path, "r")
    js_code = f.read()
    callback = CustomJS(args=dict(bsrnData=bsrnData, bsrnSelect=bsrnSelect), code=js_code)
    bsrnData.selected.js_on_change('indices', callback)

    # Plot options
    curdoc().theme = "caliber"
    makedirs("output", exist_ok=True)
    output_file("./output/" + yearMonth + "_lines.html")
    hover = HoverTool(
        tooltips=[("Date", "$x{%F %T}"), ("Value", "$y")],
        formatters={"$x": "datetime"}
    )
    tools = [hover, "pan,wheel_zoom,box_zoom,reset,save,box_select,lasso_select"]
    colors = (Plasma[8] + Colorblind[8])[:len(sensors)]

    # Lines plot
    fig = figure(
        x_axis_label="Timestamp",
        y_axis_label="W/m^2",
        x_axis_type="datetime",
        tools=tools,
        sizing_mode="stretch_both",
        title="Visual quality control")
    for (color, sensor) in zip(colors, sensors):
        fig.line("timestamp", sensor, source=bsrnData, color=color, legend_label=sensor)
    fig.legend.click_policy = "hide"

    # Scatter plot
    fig2 = figure(
        x_axis_label="Timestamp",
        y_axis_label="W/m^2",
        x_axis_type="datetime",
        tools=tools,
        sizing_mode="stretch_both",
        title="Visual quality control")
    for (color, sensor) in zip(colors, sensors):
        fig2.scatter("timestamp", sensor, source=bsrnData, color=color, legend_label=sensor)
    fig2.legend.click_policy = "hide"

    # Download button
    button_flag = Button(label="Generate data file", button_type="danger")
    with importlib.resources.path("pybsrnqc", "callbackSave.js") as data_path:
        f = open(data_path, "r")
    js_code = f.read()
    callback = CustomJS(args=dict(bsrnSelect=bsrnSelect), code=js_code)
    button_flag.js_on_event(events.ButtonClick, callback)

    # Layout
    ltab = Panel(child=fig, title="Line")
    stab = Panel(child=fig2, title="Scatter")
    tabs = Tabs(tabs=[ltab, stab])
    layout = row(tabs, column(tableData, button_flag))

    return show(layout)
