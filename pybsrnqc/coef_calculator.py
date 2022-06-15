
"""Module computing the best coefficient of a QC automatically"""

import importlib.resources
import json

from pybsrnqc import coef_study as cs
from pybsrnqc import open_data as od
from pybsrnqc import plot_limits as pl
from pybsrnqc import qc_functions as qcf
from pybsrnqc.config import Coef, Station

# Coefficients initialisation
# Get data conf from JSON file
coef = Coef()


def compute(path: str, bw_sel: str = None, station: Station = Station()):

    qc = None
    while qc not in {"QC1", "QC2", "QC3", "QC5", "QC10"}:
        qc = input("What QC do you want to study ? (QC1/QC2/QC3/QC5/QC10) :")

    level = None
    while level not in {"level_1", "level_2"}:
        level = input("What level do you want to study ? (level_1/level_2) :")

    if qc == 'QC1':
        qc = qcf.QC1()
    if qc == 'QC2':
        qc = qcf.QC2()
    if qc == 'QC3':
        qc = qcf.QC3()
    if qc == 'QC5':
        qc = qcf.QC5()
    if qc == 'QC10':
        qc = qcf.QC10()

    # Get datas
    df = od.open_all(path=path + '/', station=station)

    # Calculating kernel density for the dataset
    if qc.name in {'QC3', 'QC10'}:
        log_kernel, selected = pl.kde_computing(df, qc, select=True, bw_sel=bw_sel)
    else:
        log_kernel = pl.kde_computing(df, qc, bw_sel=bw_sel)

    # Choosing the threshold
    threshold = float(input('Threshold for outliers : '))

    # Nb of coefficients tried
    nb_try = float(input("Number of coefficients tried (200 is ok): "))

    # Field of research
    coef_range = qc.coef_range
    step = (coef_range[1] - coef_range[0]) / nb_try

    if qc.vary == 'downward_avg':
        coef_range_min = qc.coef_range_min
        step_min = (coef_range_min[1] - coef_range_min[0]) / nb_try

    # Finding the best coefficient for a density threshold given
    if qc.vary == 'downward_avg':
        if qc.name == 'QC10':
            df_score, score, df_score_min, score_min = cs.calc_coef(
                df, log_kernel, qc, threshold, level=level,
                coef_range=coef_range, coef_range_min=coef_range_min,
                step=step, step_min=step_min, selected=selected)

        else:
            df_score, score, df_score_min, score_min = cs.calc_coef(
                df, log_kernel, qc, threshold, level=level,
                coef_range=coef_range, coef_range_min=coef_range_min,
                step=step, step_min=step_min)

    elif qc.vary == 'direct_avg':
        df_score, score = cs.calc_coef(df, log_kernel, qc, threshold, level=level, coef_range=coef_range, step=step,
                                       selected=selected)
        print('Best coefficient:')
        print(score)
    else:
        df_score, score = cs.calc_coef(df, log_kernel, qc, threshold, level=level, coef_range=coef_range, step=step)
        print('Best coefficient:')
        print(score)

    # In the case there are several best scores
    if score.shape != (1, 5):
        score = score.iloc[0]
    if qc.vary == 'downward_avg':
        score_min = score_min.iloc[0]

    # Charging the new coeff
    coef.__setattr__(qc.coefficients[level], float(score[qc.coefficients[level]]))
    if qc.vary == 'downward_avg':
        coef.__setattr__(qc.coefficients[level + '_min'], float(score_min[qc.coefficients[level + '_min']]))

    # Plotting the result
    pl.plot_kde(df, log_kernel, qc, coef, level=level)

    if qc.vary == 'downward_avg':
        return qc.coefficients[level], float(score[qc.coefficients[level]]), qc.coefficients[level + '_min'], float(score_min[qc.coefficients[level + '_min']])
    else:
        return qc.coefficients[level], float(score[qc.coefficients[level]])
