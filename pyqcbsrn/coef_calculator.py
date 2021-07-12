""" Module computing the best coefficient of a QC automatically"""

# Required imports
from pyqcbsrn import open_data as od
from pyqcbsrn import qc_functions as qcf
from pyqcbsrn import plot_limits as pl
from pyqcbsrn import coef_study as cs

# Coefficients initialisation

dic_coefs = {'device': {'transactionID': 1510919492,
                        'sensorID': 'DHI_021_Avg',
                        'altitude': 97,
                        'startDay': '2020-12-01 00:00:00',
                        'endDay': '2020-12-31 23:59:00'},
             'BSRN': {'C1': 1.,
                      'D1': 0.9,
                      'C2': 0.52,
                      'D2': 0.6,
                      'C3': 0.76,
                      'D3': 0.8,
                      'C5': 330,
                      'D5': 260,
                      'C6': 465,
                      'D6': 500,
                      'C11': 0.76,
                      'D11': 0.8,
                      'C12': 11,
                      'D12': 23,
                      'C17D': 10,
                      'C18': -1.3,
                      'C19': 1},
             'cassandra': {'nodes': ['10.82.64.101', '10.82.64.102', '10.82.64.103'],
             'keyspace': 'gAAAAABfrTesyLHzrDXJbZ5XTilr9qWMaKHCQ_vjcdkHN7IoACUAxtsiZEEAId7RY9H4Bz_-Cg_xLaPUdeGu371DB7eSvy_2zw==',
             'usr': 'root',
             'license': 'BillBaoba&Co'}}


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
        print(f'Best coefficient : {score}')
    else:
        df_score, score = cs.calc_coef(df, log_kernel, QC, threshold, level=level, coef_range=coef_range, step=step)
        print(f'Best coefficient : {score}')

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