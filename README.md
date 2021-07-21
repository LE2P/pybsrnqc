# PyBsrnQC
A library for BSRN QC 

## Quick use

Put your solar data in a directory (`dataset`) for example. Under the form `YYYYMM_brut.csv`.  

Example : 

- dataset/
  - 201906_brut.csv
  - 201907_brut.csv
  - 201908_brut.csv
  - ...
  
  
  You can then study this data : 
  
  - Calculate the BSRN coefficient of a certain Quality Control chosen 
  - Create the flagged data file associated with your datas and the coefficients selected
  - Visualize the datas 
 
 ### BSRN coefficient calculation 
 
  Use the `coef_calculator` module. 
  
  ```sh
  from pyqcbsrn import coef_calculator as cc 
  
  cc.compute('./dataset')
  ```
  
  ### Quality Control tools
 
  Use the `qualitycontrol` module. You can use three functions : 
  - `automatic` which compute the flagged file 
  - `plot` which plot the data over the period 
  - `visual` which plot the data and its quality control
  
  ```sh
  from pyqcbsrn import qualitycontrol as qc 
  
  qc.automatic('./dataset/201906_brut.csv')
  qc.plot('./dataset/201906_brut.csv')
  qc.visual('./dataset/201906_brut.csv')
  ```
  
  ## A lot of other functions
  
  You can use other functions of the pyqcbsrn packages 
  For mor details go to : ???
