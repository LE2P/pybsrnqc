""" Module computing the best coefficient of a QC automatically"""

# Required imports
from pyqcbsrn import open_data as od
from pyqcbsrn import qc_functions as qcf
from pyqcbsrn import plot_limits as pl
from pyqcbsrn import coef_study as cs

import importlib.resources
import json


# Coefficients initialisation
# Get data conf from JSON file
with importlib.resources.path("pyqcbsrn", "qcrad_conf.json") as data_path:
    with open(data_path, 'r') as f:
        dic_coefs = json.load(f)


def compute(level='level_2'):

    # Choosing the QC
    QC = input('What QC do you want to study : ')
    level = input('What level do you want to study : ')

    if QC == 'QC1':
        QC = qcf.QC1()
    if QC == 'QC2':
        QC = qcf.QC2()
    if QC == 'QC3':
        QC = qcf.QC3()
    if QC == 'QC5':
        QC = qcf.QC5()
    if QC == 'QC10':
        QC = qcf.QC10()

    # Get datas
    df = od.open_all()

    # Calculating kernel density for the dataset
    if QC.name == 'QC3' or QC.name == 'QC10':
        log_kernel, selected = pl.kde_computing(df, QC, select=True)
    else:
        log_kernel = pl.kde_computing(df, QC)

    # Choosing the threshold
    threshold = float(input('Threshold for outliers : '))

    # Nb of coefficients tried
    nb_try = float(input("Number of coefficients tried (200 is ok): "))

    # Field of research
    coef_range = QC.coef_range
    step = (coef_range[1] - coef_range[0]) / nb_try

    if QC.vary == 'downward_avg':
        coef_range_min = QC.coef_range_min
        step_min = (coef_range_min[1] - coef_range_min[0]) / nb_try

    # Finding the best coefficient for a density threshold given
    if QC.vary == 'downward_avg':
        if QC.name == 'QC10':
            df_score, score, df_score_min, score_min = cs.calc_coef(df, log_kernel, QC, threshold, level=level,
                                                                    coef_range=coef_range, coef_range_min=coef_range_min,
                                                                    step=step, step_min=step_min, selected=selected)

        else:
            df_score, score, df_score_min, score_min = cs.calc_coef(df, log_kernel, QC, threshold, level=level,
                                                                    coef_range=coef_range, coef_range_min=coef_range_min,
                                                                    step=step, step_min=step_min)

    elif QC.vary == 'direct_avg':
        df_score, score = cs.calc_coef(df, log_kernel, QC, threshold, level=level, coef_range=coef_range, step=step, selected=selected)
        print('Best coefficient:')
        print(score)
    else:
        df_score, score = cs.calc_coef(df, log_kernel, QC, threshold, level=level, coef_range=coef_range, step=step)
        print('Best coefficient:')
        print(score)

    # In the case there are several best scores
    if score.shape != (1, 5):
        score = score.iloc[0]
    if QC.vary == 'downward_avg':
        score_min = score_min.iloc[0]

    # Charging the new coeff
    if QC.vary == 'downward_avg':
        dic_coefs['BSRN'][QC.coefficients[level]] = float(score[QC.coefficients[level]])
        dic_coefs['BSRN'][QC.coefficients[level + '_min']] = float(score_min[QC.coefficients[level + '_min']])
    else:
        dic_coefs['BSRN'][QC.coefficients[level]] = float(score[QC.coefficients[level]])

    # Plotting the result
    pl.plot_kde(df, log_kernel, QC, dic_coefs, level=level)

    return float(score[QC.coefficients[level]])
