# Python Bsrn Quality Control (pybsrnqc)

A library for BSRN Quality Control (QC).

Repository github with the source code : <https://github.com/LE2P/PyBsrnQC>

## Installation

Using pip

```sh
pip install pybsrnqc
```

## Quick use

Put your solar data in a directory (`dataset` for example). Data is registered in CSV files, there is a value each minute.

The data has to have at least the following columns in the header :

| timestamp | global2_avg | direct_avg | diffuse_avg | downward_avg | temperature
| :---     | :---        | :---     | :---        | :---     | :---        |
|  `2019-08-01 00:00:00` | `145.1` | `665.300` | `69.340` | `365.65` | `25` |

__Example :__

Data under the form `YYYYMM_brut.csv` with a csv file per month gathered in a directory `dataset`.

```sh
-- datastet/
   |-- 201906_brut.csv
   |-- 201907_brut.csv
   |-- 201908_brut.csv
   │-- ...
```

You can then study this data :

- Calculate the BSRN coefficient of a certain Quality Control chosen
- Create the flagged data file associated with your datas and the coefficients selected
- Visualize the datas

### Default location

Library use the Reunion Island BSRN station location by default to compute solar zenith angle (SZA).

To change location, process has following and use object `station` in the differents methods :

```python
# Exemple here for PAL BSRN station
from pybsrnqc.config import Coef, Station

station = Station()
station.LAT = 48.711951760391926
station.LON = 2.207638279957924
station.ALT = 159.0
station.TZ = "Europe/Paris"
```

### BSRN coefficient calculation

Use the `coef_calculator` module.

```python
from pybsrnqc import coef_calculator as cc 

name_coef, coef = cc.compute('./dataset')
```

You can then load your coefficient to your configuration file. Thus, your automatic control will take into account the new specific coefficient calculated.

```python
from pybsrnqc import config.Coef

my_coef = Coef()
my_coef.__setattr__(name_coef, coef)
```

If your QC have a maximum and a minimum limit (QC5 for instance) you can use the following code :

```python
from pybsrnqc import coef_calculator as cc 
from pybsrnqc import config

name_coef, coef, name_coef_min, coef_min = cc.compute('./dataset')
my_coef.__setattr__(name_coef_min, coef_min)
```

### Quality Control tool

Use the `automaticQC` module in order to generate the flagged data :

```python
from pybsrnqc.automaticQC import generateQCFiles

generateQCFiles('./dataset/201908_brut.csv')
```

Be careful : when you generate your files, it is in the same directory than you brut data. Don't forget to move your generated files if you want to continue to study your brut data.

If you want to visualize the QC of your data and your data use :

#### `plotQCFiles`

```python
from pybsrnqc.automaticQC import plotQCFiles

plotQCFiles('./dataset/201908_brut.csv')
```

#### `plotBSRN` from `visualPlot`

```python
from pybsrnqc.visualPlot import plotBSRN

plotBSRN('./dataset/201908_brut.csv')
```

### Visualization tools

You can use other functions of the pybsrnqc packages to plot and visualize the data.

#### Access to data

Inquire the path of your directory (you can select the time period over which you want to observe the data). If the period isn't specified all the files are opened.

```python
from pybsrnqc import open_data as od

df = od.open_all('./dataset')
```

If you want to specify the period, put your data under the form `YYYYMM_brut.csv` and inquire the period as`[YYYYMM, YYYYMM]`.

```python
# Example to select data from June to December 2019
df = od.open_all('./dataset',period=['201906','201912'])
```

- You can plot the data over the time period chosen with the current limits.

```python
import json 
import importlib.resources 
from pybsrnqc import plot_limits as pl
from pybsrnqc import qc_functions as qcf

# Plot the limits for the QC chosen (here QC1)
pl.limit_plot(df, qcf.QC1(), my_coef)
```

- Plotting limits with differents coefficient values

```python
# Plot the limits for the QC chosen (here QC1)
pl.multiplot_coef(df, qcf.QC1(), my_coef)
```

- Plotting the 3D histogram of the data

```python
# Plot the histogram for the QC chosen (here QC1)
pl.hist_data(df, qcf.QC1())
```

### Density analysis

#### Computation of the data density

Compute the density of each elements over the dataset given

```python
# Calculation of the KDE for a dataset
log_kernel = pl.kde_computing(df, qcf.QC1())
```

#### Time series plotting

Zoom on a certain period of time : plot on sza or time with density values.

```python
# Time series plotting and density
pl.plot_series_kde(df, log_kernel, QC, begin, end)
```

#### Coefficient indicators

Plot the evolution of certain values according to he coefficient
Return a dataframe containing the indicators values

```python
from pybsrnqc import coef_study as cs

# Indicators plotting
df_var = cs.coef_variation(df, log_kernel, qcf.QC1())
```

#### Getting the coefficient

This function give the best coefficient giving a density threshold defined as the outlier limit.
Return the score dataframe and the best score with the linked coefficient.

```python
# Coefficient calculation
df_score, score = cs.calc_coef(df, log_kernel, qcf.QC1(), threshold=-15)
```

## Small dictionary of functions

```python
open_data.open_all(path, period=None, select_day=False, select_Zenith=True, station=Station())
  # path : path of the directory with the data files
  # period : you can choose a period (see above)
  # select_day : if True, select only the hour between 5 AM and 7 PM
  # select_Zenith : if True, select only the SZA between 0° and 90°
  # station : object class Station containing station location
```

```python
plot_limits.limit_plot(df, QC, coefs, save=False, level='all', display=True, values=True, fig=True)
  # df : the dataframe studied
  # QC : the QC studied declared thanks to qc_functions
  # coefs : a set of coefficients, created with the Coef class
  # save : if True, the graph is saved
  # level : 'all' (default) to plot all the limits, 'level_2', 'level_1' or 'level_bsrn' for only one of them
  # display : if True, the graph is displayed
  # values : if True, the data elements are plotted with the limits
  # fig : if True, a new figure is created
```

```python

plot_limits.multiplot_coef(df, QC, coefs, level='level_2', coef_values=[0.0, 0.5, 1.2], level_min=None, coef_values_min=None)
  # df : the dataframe studied
  # QC : the QC studied declared thanks to qc_functions
  # coefs : a set of coefficients, created with the Coef class
  # level : 'level_2' (default) to plot the 2nd level limits, 'level_1' or 'level_bsrn' for the others
  # coef_values : the coefficient values you want to plot. Ex: [value1, value2]
  # level_min : if you want to add a lower limit, 'level_2_min' or 'level_1_min'
  # coef_values_min : the coefficient values for the lower limit
```

```python
plot_limits.hist_data(df, QC, dimension='3D')
  # df : the dataframe studied
  # QC : the QC studied declared thanks to qc_functions
  # dimension : '3D'to plot a 3D histogram, '2D' to plot a 2D one
```

```python
plot_limits.kde_computing(df, QC, display=True, coefs=None, limits=False, level='All', log_form=True, save='KDE_result', bw_sel=None)
  # df : the dataframe studied
  # QC : the QC studied declared thanks to qc_functions
  # display : if True, the graph is displayed
  # coefs : a set of coefficients, created with the Coef class
  # limits :  if True, limits are plotted on the KDE graph
  # level : 'all' (default) to plot all the limits, 'level_2', 'level_1' or 'level_bsrn' for only one of them
  # log_form : if True, the computed kernel is returned under the log form
  # save : if True, the graph is saved
  # bw_sel : bandwidth selection method. None correspond to the scott method. 'silverman'or others can be inquired.
```

```python
plot_limits.plot_series_kde(df, log_kernel, QC, begin, end, var='timestamp', line=True)
  # df : the dataframe studied
  # log_kernel : the computed KDE under the log form
  # QC : the QC studied declared thanks to qc_functions
  # begin : start date (see above)
  # end : end date (see above)
  # var : if 'timestamp' (default), time is on the abscissa. If 'SZA' it is the zenith angle
  # line : if True, dots are connected by a line
```

```python
coef_study.coef_variation(df, log_kernel, QC, level='level_2', coef_range=[0.0, 1.2], step=0.01, coef_range_min=None, step_min=None, verbose=True, display=True)
  # df : the dataframe studied
  # log_kernel : the computed KDE under the log form
  # QC : the QC studied declared thanks to qc_functions
  # level : 'level_2' (default) to plot the 2nd level limits, 'level_1' for the 1st level
  # coef_range : panel of the coefficients you want to try
  # step : step in the range
  # coef_range_min : panel of the coefficients you want to try for the lower limit
  # step_min : step in the range for the coefficient of the lower limit
  # verbose : if True, waiting point are displayed
  # display : if True, the graph is displayed
```

```python
coef_study.calc_coef(df, log_kernel, QC, threshold, level='level_2', coef_range=[0.0, 1.2], coef_range_min=[0.0, 1.2], step=0.01, step_min=0.1, verbose=True)
  # df : the dataframe studied
  # log_kernel : the computed KDE under the log form
  # QC : the QC studied declared thanks to qc_functions
  # threshold :  density threshold chosen for outliers (see above)
  # level : 'level_2' (default) to plot the 2nd level limits, 'level_1' for the 1st level
  # coef_range : panel of the coefficients you want to try
  # step : step in the range
  # coef_range_min : panel of the coefficients you want to try for the lower limit
  # step_min : step in the range for the coefficient of the lower limit
  # verbose : if True, waiting point are displayed
```

```python
coef_calculator.compute(path=None, level='level_2', bw_sel=None, station=Station())
  # path : path of the directory with the data files
  # level : 'level_2' (default) to plot the 2nd level limits, 'level_1' for the 1st level
  # bw_sel : bandwidth selection method. None correspond to the scott method. 'silverman' or others can be inquired.
  # station : object class Station containing station location
```
