"""
Module that plot the curves following the quality controle equations
 """
import os
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.path import Path
from matplotlib.widgets import LassoSelector
from scipy import stats

from pybsrnqc.config import Coef

# -----------------------------------------------------------------------------------------------------------
# Plots of the BSRN limits on datasets


def limit_plot(df, QC, coef: Coef, save: bool = False, level='all', display: bool = True,
               values: bool = True, fig: bool = True):

    """ Function plotting the limit curves and the dataset points of a
        dataframe"""

    df = df[['timestamp', QC.varx, QC.vary]]

    X_val1 = np.array(df[QC.varx])
    X_val2 = np.array(df[QC.vary])

    lim_l1 = []
    lim_l2 = []
    lim_bsrn = []

    lim_l1_min = []
    lim_l2_min = []
    lim_bsrn_min = []

    val1_var = list(X_val1)
    val2_var = list(X_val2)

    for VAL1, VAL2 in zip(X_val1, X_val2):

        if QC.vary == 'downward_avg':

            l1, l2, l_bsrn, l1_min, l2_min, l_bsrn_min = QC.f(VAL2, VAL1, coef)

            lim_l1_min.append(l1_min)
            lim_l2_min.append(l2_min)
            lim_bsrn_min.append(l_bsrn_min)

        else:

            l1, l2, l_bsrn = QC.f(VAL2, VAL1, coef)

        lim_l1.append(l1)
        lim_l2.append(l2)
        lim_bsrn.append(l_bsrn)

    if fig:
        plt.figure(figsize=(20, 14))

    if values:
        plt.scatter(val1_var, val2_var, marker='+', color='dodgerblue',
                    label='Values', s=1)

    if level == 'level_1' or level == 'all':
        plt.scatter(val1_var, lim_l1, marker='+', color='green',
                    label=f"1rst level limit - {coef.__getattribute__(QC.coefficients['level_1'])}", s=1)
    if level == 'level_2' or level == 'all':
        plt.scatter(val1_var, lim_l2, marker='+', color='blue',
                    label=f"2nd level limit - {coef.__getattribute__(QC.coefficients['level_2'])}", s=1)
    if level == 'level_bsrn' or level == 'all':
        plt.scatter(val1_var, lim_bsrn, marker='+', color='red', label="BSRN  limit", s=1)

    if QC.vary == 'downward_avg':

        if level == 'level_1' or level == 'all':
            plt.scatter(val1_var, lim_l1_min, marker='+', color='lightgreen',
                        label=f"1rst level limit - {coef.__getattribute__(QC.coefficients['level_1_min'])}", s=1)
        if level == 'level_2' or level == 'all':
            plt.scatter(val1_var, lim_l2_min, marker='+', color='lightblue',
                        label=f"2nd level limit - {coef.__getattribute__(QC.coefficients['level_2_min'])}", s=1)
        if level == 'level_bsrn' or level == 'all':
            plt.scatter(val1_var, lim_bsrn_min, marker='+', color='lightcoral', label="BSRN  limit", s=1)

    if save:
        plt.savefig(f'limit_plot - {QC.vary} versus {QC.varx}')
    if display:
        plt.xlabel(QC.unitx,)
        plt.ylabel(QC.unity)
        plt.title(f'Limits - {QC.vary}', fontsize=20)
        plt.legend(prop={'size': 15})
        plt.show()


def multiplot_coef(df, QC, coef, level='level_2', coef_values=[0.0, 0.5, 1.2], level_min=None, coef_values_min=None):
    'Dessine la courbe limite pour plusieurs valeurs du coefficients'

    X_val1 = np.array(df[QC.varx])
    X_val2 = np.array(df[QC.vary])

    val1_var = list(X_val1)
    val2_var = list(X_val2)

    plt.figure(figsize=(20, 14))
    plt.scatter(val1_var, val2_var, marker='+', color='dodgerblue',
                label='Values', s=1)

    for v in coef_values:

        # We compute the considered coefficient
        coef.__setattr__(QC.coefficients[level], v)

        # We plot for this coefficient
        limit_plot(df, QC, coef, level=level, display=False, values=False, fig=False)

    if coef_values_min is not None:
        for v in coef_values_min:

            # We compute the considered coefficient
            coef.__setattr__(QC.coefficients[level_min], v)

            # We plot for this coefficient
            limit_plot(df, QC, coef, level=level, display=False, values=False, fig=False)

    plt.xlabel(QC.unitx)
    plt.ylabel(QC.unity)
    plt.title(f'Limits - {QC.vary}', fontsize=20)
    plt.legend(prop={'size': 15})
    plt.show()


# ----------------------------------------------------------------------------------------------------------------------
# Displaying of the data histograms in 2D and 3D. It allows us to see the
# shape of the data and its caracteristics like unimodality

def hist_data(df, QC, dimension='3D'):

    # Get the data
    x = np.array(df[[QC.vary, QC.varx]])

    # Create the figure
    fig = plt.figure(figsize=(20, 14))
    ax = fig.add_subplot(projection='3d')

    hist, xedges, yedges = np.histogram2d(x[:, 0], x[:, 1], bins=75)

    # Construct arrays for the anchor positions of the 16 bars.
    xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25, indexing="ij")
    xpos = xpos.ravel()
    ypos = ypos.ravel()
    zpos = 0

    # Construct arrays with the dimensions for the 16 bars.
    dx = xedges[-1] / 75 * np.ones_like(zpos)
    dy = yedges[-1] / 75 * np.ones_like(zpos)
    dz = hist.ravel()

    cmap = plt.cm.get_cmap('Wistia')  # Get desired colormap - you can change this
    max_height = np.max(dz)   # get range of colorbars so we can normalize
    min_height = np.min(dz)
    # scale each z to [0,1], and get their rgb values
    rgba = [cmap((k - min_height) / max_height) for k in dz]

    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=rgba, zsort='average')

    plt.title(f'Data histogram - {QC.vary} vs {QC.varx}', fontdict={'fontsize': 20})
    plt.xlabel(QC.unity)
    plt.ylabel(QC.unitx)
    ax.set_zlabel('Number of samples')
    plt.show()


# --------------------------------------------------------------------------------------------
# KDE computation and plotting for our dataset


def kde_computing(df, QC, display=True, coef: Coef = None, limits=False, level='All',
                  log_form=True, save='KDE_result', select=False, bw_sel=None):

    # Get the data
    X = np.array(df[[QC.vary, QC.varx]]).T
    # Kernel calculation
    print('Computing kde - It can take some times')

    kernel = stats.gaussian_kde(X, bw_method=bw_sel)(X)
    kernel_log = np.log(kernel)

    # Plot
    if display:

        fig, ax = plt.subplots(figsize=(20, 14))
        pts = plt.scatter(X[1, :], X[0, :], c=kernel_log, s=1, cmap=plt.cm.jet)
        selector = SelectFromCollection(ax, pts)

    if limits:
        limit_plot(df, QC, coef, save=False, level='all', display=False, values=False, fig=False)

    if display:
        if select:
            if QC.name == 'QC3' or QC.name == 'QC10':

                def accept(event):
                    if event.key == "enter":
                        # print("Selected points:")
                        selected = selector.xys[selector.ind].tolist()
                        with open("selected.txt", "wb") as fp:   # Pickling
                            pickle.dump(selected, fp)
                        # print(selected)
                        # print(type(selected))
                        selector.disconnect()
                        ax.set_title("", fontsize=20)
                        fig.canvas.draw()

                fig.canvas.mpl_connect("key_press_event", accept)
            ax.set_title("Press enter to accept selected points.", fontsize=20)

        ax.set_xlabel(QC.unitx)
        ax.set_ylabel(QC.unity)
        if select:
            if QC.name == 'QC3' or QC.name == 'QC10':
                ax.set_title(f"{QC.vary} density along {QC.varx} \n Select the points that you don't want to consider", fontsize=20)
        else:
            ax.set_title(f'{QC.vary} density along {QC.varx}', fontsize=20)
        plt.colorbar(pts, label='Density Log(KDE)')
        ax.legend(prop={'size': 15})
        plt.show()

    # Download file
    if save is not None:
        pd.DataFrame(kernel).to_csv(save + '.csv')

    # Return density
    if log_form:
        if select:
            if QC.name == 'QC3' or QC.name == 'QC10':
                with open("selected.txt", "rb") as fp:   # Unpickling
                    selected = pickle.load(fp)
                os.remove("selected.txt")
                return kernel_log, selected
        else:
            return kernel_log
    else:
        if select:
            if QC.name == 'QC3' or QC.name == 'QC10':
                with open("selected.txt", "rb") as fp:   # Unpickling
                    selected = pickle.load(fp)
                os.remove("selected.txt")
                return kernel, selected
        else:
            return kernel


def plot_kde(df, log_kernel, QC, coef: Coef, level='level_2'):

    plt.figure(figsize=(20, 14))

    # Get the data
    X = np.array(df[[QC.vary, QC.varx]]).T

    # Plot the data
    plot = plt.scatter(X[1, :], X[0, :], c=log_kernel, s=1, cmap=plt.cm.jet)

    if level is not None:
        limit_plot(df, QC, coef, save=False, level=level, display=False, values=False, fig=False)

    plt.xlabel(QC.unitx)
    plt.ylabel(QC.unity)
    plt.title(f'{QC.vary} density along {QC.varx}', fontsize=20)
    plt.colorbar(plot, label='Density Log(KDE)')
    plt.legend(prop={'size': 15})
    plt.show()


def plot_series_kde(df, log_kernel, QC, begin, end, var='timestamp', line=True):

    df['log_kde'] = log_kernel
    kernel_range = [np.min(log_kernel), np.max(log_kernel)]
    mask = (df['timestamp'] >= begin) & (df['timestamp'] < end)
    df_week = df.loc[mask]

    if var == 'SZA':
        tick = None
    else:
        tick = np.arange(0, len(list(df_week[var])), 60)

    plt.figure(figsize=(20, 14))

    if line:
        plt.plot(list(df_week[var]), list(df_week[QC.vary]),
                 color='black', alpha=0.2)

    plot = plt.scatter(list(df_week[var]), list(df_week[QC.vary]),
                       c=np.array(df_week['log_kde']), cmap=plt.cm.jet, s=5)

    plt.xlabel(var)
    plt.ylabel(QC.unity)
    plt.xticks(tick, rotation=45)
    plt.title(f'{QC.vary} and its density - {begin}', fontsize=20)
    plt.clim(kernel_range[0], kernel_range[1])
    plt.colorbar(plot, label='Density Log(KDE)')
    plt.show()


# -----------------------------------------------
# Lasso used to select the datas

class SelectFromCollection:
    """
    Select indices from a matplotlib collection using `LassoSelector`.

    Selected indices are saved in the `ind` attribute. This tool fades out the
    points that are not part of the selection (i.e., reduces their alpha
    values). If your collection has alpha < 1, this tool will permanently
    alter the alpha values.

    Note that this tool selects collection objects based on their *origins*
    (i.e., `offsets`).

    Parameters
    ----------
    ax : `~matplotlib.axes.Axes`
        Axes to interact with.
    collection : `matplotlib.collections.Collection` subclass
        Collection you want to select from.
    alpha_other : 0 <= float <= 1
        To highlight a selection, this tool sets all selected points to an
        alpha value of 1 and non-selected points to *alpha_other*.
    """

    def __init__(self, ax, collection, alpha_other=0.3):
        self.canvas = ax.figure.canvas
        self.collection = collection
        self.alpha_other = alpha_other

        self.xys = collection.get_offsets()
        self.Npts = len(self.xys)

        # Ensure that we have separate colors for each object
        self.fc = collection.get_facecolors()
        if len(self.fc) == 0:
            raise ValueError('Collection must have a facecolor')
        elif len(self.fc) == 1:
            self.fc = np.tile(self.fc, (self.Npts, 1))

        self.lasso = LassoSelector(ax, onselect=self.onselect)
        self.ind = []

    def onselect(self, verts):
        path = Path(verts)
        self.ind = np.nonzero(path.contains_points(self.xys))[0]
        self.fc[:, -1] = self.alpha_other
        self.fc[self.ind, -1] = 1
        self.collection.set_facecolors(self.fc)
        self.canvas.draw_idle()

    def disconnect(self):
        self.lasso.disconnect_events()
        self.fc[:, -1] = 1
        self.collection.set_facecolors(self.fc)
        self.canvas.draw_idle()
