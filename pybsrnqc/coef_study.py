"""
Module that compute the coefficients regarding the historical data
 """

import importlib.resources
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from pybsrnqc.config import Coef 

# -----------------------------------------------------------------------------------------------------------
# Initialisation of a set of coefficients
# Get data conf from JSON file

dic_coefs = Coef()
# ------------------------------------------------------------------------------------------------------------


def coef_variation(df, log_kernel, QC, level='level_2', coef_range=[0.0, 1.2], step=0.01, coef_range_min=None, step_min=None, verbose=True, display=True):

    """ Function which calculates certain indicators
    according to the value of the coefficient """

    # Creation of the dataframe containing the KDE values
    df['log_kde'] = log_kernel
    df_min = df.copy()
    df_min = df_min.loc[df_min['downward_avg'] <= 400]

    # Name of the coefficient we study
    coef_name = QC.coefficients[level]

    # Values of the coefficients we study
    values_c = list(np.arange(coef_range[0], coef_range[1], step))

    # Initialisation of the indicators
    the_coefs = []
    nb_out = []
    kde_means = []
    kde_sums = []
    kde_stds = []

    if QC.vary == 'downward_avg':

        coef_name_min = QC.coefficients[level + '_min']
        values_c_min = list(np.arange(coef_range_min[0], coef_range_min[1], step_min))

        # Initialisation of the indicators
        the_coefs_min = []
        nb_out_min = []
        kde_means_min = []
        kde_sums_min = []
        kde_stds_min = []

    # Visualization of the computation
    if verbose:
        for k in range(len(values_c)):
            print('.', end='')
        print()

    # Calculus of the indicators for each coefficients
    for coef in values_c:

        # Generation of the new coefficients

        dic = Coef()
        dic.__setattr__(coef_name, coef)

        # Generation of the outliers according to the limits linked to the coefficients

        df_lim = df.copy()
        df_lim['flag'] = QC.calc_lim(df, coef=dic)[3]
        df_lim['out_coef'] = np.array([0] * df_lim.shape[0])
        df_lim.loc[df_lim.flag == 4, "out_coef"] = 1

        df_lim_out = df_lim.loc[df_lim['out_coef'] == 1]
        kde_mean = df_lim_out['log_kde'].mean()
        kde_sum = df_lim_out['log_kde'].sum()
        kde_std = df_lim_out['log_kde'].std()

        nb_out.append(df_lim['out_coef'].sum())
        kde_means.append(kde_mean)
        kde_sums.append(kde_sum)
        the_coefs.append(coef)
        kde_stds.append(kde_std)

        # Visualization of the computation
        print('-', end='')

    if QC.vary == 'downward_avg':
        for coef_min in values_c_min:

            # Generation of the new coefficients
            dic = Coef()
            dic.__setattr__(coef_name_min, coef_min)

            # Generation of the outliers according to the limits linked to the coefficients
            df_lim = df_min.copy()
            df_lim['flag'] = QC.calc_lim(df_min, coef=dic)[3]
            df_lim['out_coef'] = np.array([0] * df_lim.shape[0])
            df_lim.loc[df_lim.flag == 3, "out_coef"] = 1

            df_lim_out = df_lim.loc[df_lim['out_coef'] == 1]
            kde_mean = df_lim_out['log_kde'].mean()
            kde_sum = df_lim_out['log_kde'].sum()
            kde_std = df_lim_out['log_kde'].std()

            nb_out_min.append(df_lim['out_coef'].sum())
            kde_means_min.append(kde_mean)
            kde_sums_min.append(kde_sum)
            the_coefs_min.append(coef_min)
            kde_stds_min.append(kde_std)

            # Visualization of the computation
            print('-', end='')

    tab = np.zeros((len(values_c), 4))
    df_var = pd.DataFrame(tab)
    df_var['nb_out'] = nb_out
    df_var['kde_mean'] = kde_means
    df_var['kde_sum'] = kde_sums
    df_var['coefs'] = the_coefs
    df_var['std'] = kde_stds
    df_var = df_var.drop([0, 1, 2, 3], axis=1)

    # Display the plot
    if display:

        plt.figure(figsize=(20, 14))

        # Number of values removed
        ax1 = plt.subplot(221)
        ax1.plot(df_var['coefs'], df_var['nb_out'])
        ax1.set_xlabel('Coefficients')
        ax1.set_ylabel('Number of values removed')
        ax1.set_title('Number of outlier according to the coefficient')

        # KDE Mean
        ax2 = plt.subplot(222)
        ax2.plot(df_var['coefs'], df_var['kde_mean'])
        ax2.set_xlabel('Coefficients')
        ax2.set_ylabel('KDE Mean')
        ax2.set_title('Kde mean of the outliers according to the coefficient')

        # KDE Mean vs nb_out
        ax3 = plt.subplot(223)
        ax3.plot(df_var['nb_out'], df_var['kde_mean'])
        ax3.set_xlabel('Number of values removed')
        ax3.set_ylabel('KDE Mean')
        ax3.set_title('Kde mean of the outliers versus number of values removed')

        # KDE std versus coefs
        ax4 = plt.subplot(224)
        ax4.plot(df_var['coefs'], df_var['std'])
        ax4.set_xlabel('Coefficients')
        ax4.set_ylabel('KDE std')
        ax4.set_title('Kde standard deviation according to the coefficients')

        plt.show()

    if QC.vary == 'downward_avg':

        tab = np.zeros((len(values_c_min), 4))
        df_var_min = pd.DataFrame(tab)
        df_var_min['nb_out'] = nb_out_min
        df_var_min['kde_mean'] = kde_means_min
        df_var_min['kde_sum'] = kde_sums_min
        df_var_min['coefs'] = the_coefs_min
        df_var_min['std'] = kde_stds_min
        df_var_min = df_var_min.drop([0, 1, 2, 3], axis=1)

        # Display the plot
        if display:

            plt.figure(figsize=(20, 14))

            # Number of values removed
            ax1 = plt.subplot(221)
            ax1.plot(df_var_min['coefs'], df_var_min['nb_out'])
            ax1.set_xlabel('Coefficients')
            ax1.set_ylabel('Number of values removed')
            ax1.set_title('Number of outlier according to the coefficient')

            # KDE Mean
            ax2 = plt.subplot(222)
            ax2.plot(df_var_min['coefs'], df_var_min['kde_mean'])
            ax2.set_xlabel('Coefficients')
            ax2.set_ylabel('KDE Mean')
            ax2.set_title('Kde mean of the outliers according to the coefficient')

            # KDE Mean vs nb_out
            ax3 = plt.subplot(223)
            ax3.plot(df_var_min['nb_out'], df_var_min['kde_mean'])
            ax3.set_xlabel('Number of values removed')
            ax3.set_ylabel('KDE Mean')
            ax3.set_title('Kde mean of the outliers versus number of values removed')

            # KDE std versus coef
            ax4 = plt.subplot(224)
            ax4.plot(df_var_min['coefs'], df_var_min['std'])
            ax4.set_xlabel('Coefficients')
            ax4.set_ylabel('KDE std')
            ax4.set_title('Kde standard deviation according to the coefficients')

            plt.title('Indicators relative to the minimum limits')
            plt.show()

            return df_var, df_var_min

    return df_var


def threshold_var(df, log_kernel, threshold_range=None, step=0.1, display=True):

    if threshold_range is None:

        threshold_range = [np.min(log_kernel), np.max(log_kernel)]

    values_t = list(np.arange(threshold_range[0], threshold_range[1], step))

    # Gettinf KDE density
    df['log_kde'] = log_kernel

    # Initialisation
    nb_out_density = []

    for threshold in values_t:

        df['out_density'] = np.array([0] * df.shape[0])
        df['out_density_min'] = np.array([0] * df.shape[0])

        # Labeling according to the chosen threshold
        df.loc[df.log_kde <= threshold, "out_density"] = 1
        df_min = df.copy()
        df_min.loc[(df['downward_avg'] <= 350) & (df.log_kde <= threshold), 'out_density_min'] = 1

        nb_out_density.append(df['out_density'].sum())

    tab = np.zeros((len(values_t), 1))
    df_var = pd.DataFrame(tab)
    df_var['nb_out_density'] = nb_out_density
    df_var['thresholds'] = values_t
    df_var = df_var.drop([0], axis=1)

    if display:

        plt.figure(figsize=(20, 14))
        plt.plot(df_var['thresholds'], df_var['nb_out_density'])
        plt.title('Number of elements removed according to a threshold')
        plt.xlabel('Threshold')
        plt.ylabel('Removed values')
        plt.show()

    return df_var


# ---------------------------------------------------------------------------------------------------------------------

def calc_coef(df, log_kernel, QC, threshold, level='level_2', coef_range=[0.0, 1.2], coef_range_min=[0.0, 1.2], step=0.01, step_min=0.1, verbose=True, selected=None):

    # Labeling according to the chosen threshold
    df['log_kde'] = log_kernel
    df['out_density'] = np.array([0] * df.shape[0])
    df['out_density_min'] = np.array([0] * df.shape[0])
    df.loc[df.log_kde <= threshold, "out_density"] = 1
    df.loc[(df['downward_avg'] <= 350) & (df.log_kde <= threshold), 'out_density_min'] = 1

    # Values of the coefficients tested
    values_c = list(np.arange(coef_range[0], coef_range[1], step))

    # Name of the coefficient we study
    coef_name = QC.coefficients[level]

    # Adding a constraint for QC3 and QC10
    if QC.name == 'QC3' or QC.name == 'QC10':
        # We precise that points under a certain limit are not ouliers
        dic = Coef()
        dic.__setattr__(coef_name, 0.6)

        for el in selected:
            df.loc[(df['temperature'] == el[0]) & (df[QC.vary] == el[1]), 'out_density'] = 0

    # Score initialisation
    a_scores = []
    p_scores = []
    r_scores = []
    f_scores = []

    if QC.vary == 'downward_avg':
        coef_name_min = QC.coefficients[level + '_min']
        values_c_min = list(np.arange(coef_range_min[0], coef_range_min[1], step_min))
        a_scores_min = []
        p_scores_min = []
        r_scores_min = []
        f_scores_min = []

    # Verbose
    if verbose:
        for k in range(len(values_c)):
            print('.', end='')
        print()

    for coef in values_c:

        if verbose:
            print('-', end='')

        # Generation of coefficient
        dic = Coef()
        dic.__setattr__(coef_name, coef)

        # Generation of the outliers according to the equations and the density

        df_lim = df.copy()
        df_lim['flag'] = QC.calc_lim(df, coef=dic)[3]

        if level == 'level_2':
            df_lim['out_coef'] = np.array([0] * df_lim.shape[0])
            df_lim.loc[df_lim.flag == 4, "out_coef"] = 1
        else:
            df_lim['out_coef'] = np.array([0] * df_lim.shape[0])
            df_lim.loc[(df_lim.flag == 2) | (df_lim.flag == 4), "out_coef"] = 1

        a_scores.append(accuracy_score(df['out_density'], df_lim['out_coef']))
        p_scores.append(precision_score(df['out_density'], df_lim['out_coef'], zero_division=0))
        r_scores.append(recall_score(df['out_density'], df_lim['out_coef'], zero_division=0))
        f_scores.append(f1_score(df['out_density'], df_lim['out_coef'], zero_division=0))

    if QC.vary == 'downward_avg':

        for coef_min in values_c_min:

            # Generation of coefficient

            dic = Coef()
            dic.__setattr__(coef_name_min, coef_min)

            # Generation of the outliers according to the equations and the density

            df_lim = df.copy()
            df_lim['flag'] = QC.calc_lim(df, coef=dic)[3]

            if level == 'level_2':
                df_lim['out_coef'] = np.array([0] * df_lim.shape[0])
                df_lim.loc[df_lim.flag == 3, "out_coef"] = 1
            else:
                df_lim['out_coef'] = np.array([0] * df_lim.shape[0])
                df_lim.loc[(df_lim.flag == 1) | (df_lim.flag == 3), "out_coef"] = 1

            a_scores_min.append(accuracy_score(df['out_density'],
                                df_lim['out_coef']))
            p_scores_min.append(precision_score(df['out_density'], df_lim['out_coef'], zero_division=0))
            r_scores_min.append(recall_score(df['out_density'], df_lim['out_coef'], zero_division=0))
            f_scores_min.append(f1_score(df['out_density'], df_lim['out_coef'], zero_division=0))

    # Creation of the scores dataframe

    tab = np.zeros((len(values_c), 4))
    df_scores = pd.DataFrame(tab)
    df_scores[coef_name] = values_c
    df_scores['accuracy_score'] = a_scores
    df_scores['precision_score'] = p_scores
    df_scores['recall_score'] = r_scores
    df_scores['f1_score'] = f_scores
    df_scores = df_scores.drop([0, 1, 2, 3], axis=1)

    # Getting the coefficient with the best score
    f1_max = df_scores['f1_score'].max()
    line_max = df_scores.loc[df_scores['f1_score'] == f1_max]

    if QC.vary == 'downward_avg':

        tab = np.zeros((len(values_c_min), 4))
        df_scores_min = pd.DataFrame(tab)

        df_scores_min[coef_name_min] = values_c_min
        df_scores_min['accuracy_score'] = a_scores_min
        df_scores_min['precision_score'] = p_scores_min
        df_scores_min['recall_score'] = r_scores_min
        df_scores_min['f1_score'] = f_scores_min
        df_scores_min = df_scores_min.drop([0, 1, 2, 3], axis=1)

        # Getting the coefficient with the best score
        f1_max_min = df_scores_min['f1_score'].max()
        line_max_min = df_scores_min.loc[df_scores_min['f1_score'] == f1_max_min]

    # Print the coefficient
    print()
    print('Upper limit')
    print(line_max)

    if QC.vary == 'downward_avg':
        print()
        print('Lower limit')
        print(line_max_min)

        return df_scores, line_max, df_scores_min, line_max_min

    return df_scores, line_max
