# PyBsrnQC
A library for BSRN Quality Control (QC)

Repository github with the source code : https://github.com/LE2P/PyBsrnQC

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
- dataset/
  - 201906_brut.csv
  - 201907_brut.csv
  - 201908_brut.csv
  - ...
  ```

  
You can then study this data : 
  
- Calculate the BSRN coefficient of a certain Quality Control chosen 
- Create the flagged data file associated with your datas and the coefficients selected
- Visualize the datas 
 
 ### BSRN coefficient calculation 
 
  Use the `coef_calculator` module. 
  
  ```sh
  from pyqcbsrn import coef_calculator as cc 
  
  name_coef, coef = cc.compute('./dataset')
  ```
  
  You can then load your coefficient to your configuration file. Thus, your automatic control will take into account the new specific coefficient calculated.
  
  ```sh
  from pyqcbsrn import config
  
  config.load(name_coef, coef)
  ```
  If your QC have a maximum and a minimum limit (QC5 for instance) you can use the following code : 
  
  ```sh
  from pyqcbsrn import coef_calculator as cc 
  from pyqcbsrn import config
  
  name_coef, coef, name_coef_min, coef_min = cc.compute('./dataset')
  config.load(name_coef, coef, name_coef_min, coef_min)
  ```
  
  ### Quality Control tool
 
  Use the `automaticQC` module in order to generate the flagged data : 
  
  ```sh
  from pyqcbsrn.automaticQC import generateQCFiles
  
generateQCFiles('./dataset/201908_brut.csv')
  ```
  Be careful : when you generate your files, it is in the same directory than you brut data. Don't forget to move your generated files if you want to continue to study your brut data.
  
  If you want to visualize the QC of your data and your data use : 
  - `plotQCFiles`  
     
    ```sh
    from pyqcbsrn.automaticQC import plotQCFiles

    plotQCFiles('./dataset/201908_brut.csv')
      ```
  - `plotBSRN` from `visualPlot`
     ```sh
      from pyqcbsrn.visualPlot import plotBSRN

      plotBSRN('./dataset/201908_brut.csv')
     ```

  ### Visualization tools 
  
  You can use other functions of the pyqcbsrn packages to plot and visualize the data.
  
  * Access to data 

    Inquire the path of your directory (you can select the time period over which you want to observe the data). If the period isn't specified all the files are opened.

    ```sh
    from pyqcbsrn import open_data as od

    df = od.open_all('./dataset')
    ```
     If you want to specify the period, put your data under the form `YYYYMM_brut.csv` and inquire the period as`[YYYYMM, YYYYMM]`. 

     ```sh
      # Example to select data from June to December 2019

      df = od.open_all('./dataset',period=['201906','201912'])
     ```

  * You can plot the data over the time period chosen with the current limits.


    ```sh

    import json 
    from pyqcbsrn import plot_limits as pl
    from pyqcbsrn import qc_functions as qcf

    # Get data conf from JSON file
    with importlib.resources.path("pyqcbsrn", "qcrad_conf.json") as data_path:
    with open(data_path, 'r') as f:
        coefs = json.load(f)

    # Plot the limits for the QC chosen (here QC1)
    pl.limit_plot(df, qcf.QC1(), coefs)

    ```
* Plotting limits with differents coefficient values

  ```sh
  
  # Plot the limits for the QC chosen (here QC1)
  pl.multiplot_coef(df, qcf.QC1(), coefs)
 
  ```

* Plotting the 3D histogram of the data 

  ```sh
  
  # Plot the histogram for the QC chosen (here QC1)
  pl.hist_data(df, qcf.QC1())
 
  ```
  
 ### Density analysis
  
 * Computation of the data density 
   Compute the density of each elements over the dataset given
   ```sh
  
    # Calculation of the KDE for a dataset
    log_kernel = pl.kde_computing(df, qcf.QC1())

    ```
  
 * Time series plotting
   Zoom on a certain period of time : plot on sza or time with density values.
    
   ```sh
  
   # Time series plotting and density
   pl.plot_series_kde(df, log_kernel, QC, begin, end)
   ```
    
 * Coefficient indicators 
   Plot the evolution of certain values according to he coefficient 
   Return a dataframe containing the indicators values
    
   ```sh
   from pyqcbsrn import coef_study as cs
    
   # Indicators plotting
   df_var = cs.coef_variation(df, log_kernel, qcf.QC1())
   ```
    
 * Getting the coefficient 
   This function give the best coefficient giving a density threshold defined as the outlier limit.
   Return the score dataframe and the best score with the linked coefficient.
    
   ```sh
   # Coefficient calculation
   df_score, score = cs.calc_coef(df, log_kernel, qcf.QC1(), threshold=-15)
   ```
