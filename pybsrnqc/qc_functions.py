"""
Module that provides the QC class with their assiocated functions and labeling
"""

import math

import numpy as np

import pybsrnqc.qcrad as qcr
from pybsrnqc.config import Coef


def gen_calc_lim(self, df, coef: Coef):
    """ Computation of the limits and the labels of a dataframe"""

    df = df[['timestamp', self.varx, self.vary]]

    X_val1 = np.array(df[self.varx])
    X_val2 = np.array(df[self.vary])

    lim_l1 = []
    lim_l2 = []
    lim_bsrn = []

    lim_l1_min = []
    lim_l2_min = []
    lim_bsrn_min = []

    labels = []

    for VAL1, VAL2 in zip(X_val1, X_val2):

        if self.vary == 'downward_avg':

            l1, l2, l_bsrn, l1_min, l2_min, l_bsrn_min = self.f(VAL2, VAL1, coef)

            lim_l1_min.append(l1_min)
            lim_l2_min.append(l2_min)
            lim_bsrn_min.append(l_bsrn_min)

        else:

            l1, l2, l_bsrn = self.f(VAL2, VAL1, coef)

        label = self.lab(VAL2, VAL1, coef)

        lim_l1.append(l1)
        lim_l2.append(l2)
        lim_bsrn.append(l_bsrn)
        labels.append(label)

    if self.vary == 'downward_avg':
        return lim_l1, lim_l2, lim_bsrn, labels, lim_l1_min, lim_l2_min, lim_bsrn_min
    else:
        return lim_l1, lim_l2, lim_bsrn, labels

# Definition of the QC class


class QC1:

    def __init__(self):
        self.name = 'QC1'
        self.varx = 'SZA'
        self.vary = 'global2_avg'
        self.unitx = 'SZA'
        self.unity = 'W.m-2'
        self.coefficients = {'level_1': 'C1', 'level_2': 'D1'}
        self.coef_range = [0.0, 1.2]

    @staticmethod
    def f(GSW, SZA, coef: Coef):
        ''' Return the 2 main variables, the 1rst level limit, the 2nd level limit and the physical limit for a sample'''

        l1 = qcr.REF.SOLAR_CONSTANT * coef.C1 * math.pow(math.cos(math.radians(SZA)), 1.2) + 50
        l2 = qcr.REF.SOLAR_CONSTANT * coef.D1 * math.pow(math.cos(math.radians(SZA)), 1.2) + 55
        l_bsrn = qcr.REF.SOLAR_CONSTANT * 1.5 * math.pow(math.cos(math.radians(SZA)), 1.2) + 100

        return l1, l2, l_bsrn

    @staticmethod
    def lab(GSW, SZA, coef: Coef):
        return qcr.QC1(GSW, SZA, coef)

    def calc_lim(self, df, coef: Coef):
        return gen_calc_lim(self, df, coef)


class QC2:

    def __init__(self):
        self.name = 'QC2'
        self.varx = 'SZA'
        self.vary = 'diffuse_avg'
        self.unitx = 'SZA'
        self.unity = 'W.m-2'
        self.coefficients = {'level_1': 'C2', 'level_2': 'D2'}
        self.coef_range = [0.0, 1.0]

    @staticmethod
    def f(Dif, SZA, coef: Coef):
        ''' Return the 2 main variables, the 1rst level limit, the 2nd level limit and the physical limit for a sample'''

        l1 = qcr.REF.SOLAR_CONSTANT * coef.C2 * math.pow(math.cos(math.radians(SZA)), 1.2) + 30
        l2 = qcr.REF.SOLAR_CONSTANT * coef.D2 * math.pow(math.cos(math.radians(SZA)), 1.2) + 35
        l_bsrn = qcr.REF.SOLAR_CONSTANT * 0.95 * math.pow(math.cos(math.radians(SZA)), 1.2) + 50

        return l1, l2, l_bsrn

    @staticmethod
    def lab(Dif, SZA, coef: Coef):
        return qcr.QC2(Dif, SZA, coef)

    def calc_lim(self, df, coef: Coef):
        return gen_calc_lim(self, df, coef)


class QC3:

    def __init__(self):
        self.name = 'QC3'
        self.varx = 'SZA'
        self.vary = 'direct_avg'
        self.unitx = 'SZA'
        self.unity = 'W.m-2'
        self.coefficients = {'level_1': 'C3', 'level_2': 'D3'}
        self.coef_range = [0.0, 1.0]

    @staticmethod
    def f(DirN, SZA, coef: Coef):
        ''' Return the 2 main variables, the 1rst level limit, the 2nd level limit and the physical limit for a sample'''

        l1 = qcr.REF.SOLAR_CONSTANT * coef.C3 * math.pow(math.cos(math.radians(SZA)), 0.2) + 10
        l2 = qcr.REF.SOLAR_CONSTANT * coef.D3 * math.pow(math.cos(math.radians(SZA)), 0.2) + 15
        l_bsrn = qcr.REF.SOLAR_CONSTANT

        return l1, l2, l_bsrn

    @staticmethod
    def lab(DirN, SZA, coef: Coef):
        return qcr.QC3(DirN, SZA, coef)

    def calc_lim(self, df, coef: Coef):
        return gen_calc_lim(self, df, coef)


class QC5:

    def __init__(self):
        self.name = 'QC5'
        self.varx = 'SZA'
        self.vary = 'downward_avg'
        self.unitx = 'SZA'
        self.unity = 'W.m-2'
        self.coefficients = {'level_1_min': 'C5', 'level_2_min': 'D5', 'level_1': 'C6', 'level_2': 'D6'}
        self.coef_range = [400.0, 600.0]
        self.coef_range_min = [200.0, 400.0]

    @staticmethod
    def f(LWdn, SZA, coef: Coef):
        ''' Return the 2 main variables, the 1rst level limit, the 2nd level limit and the physical limit for a sample'''

        l1_max = coef.C6
        l2_max = coef.D6
        l_bsrn_max = 700

        l1_min = coef.C5
        l2_min = coef.D5
        l_bsrn_min = 40

        return l1_max, l2_max, l_bsrn_max, l1_min, l2_min, l_bsrn_min

    @staticmethod
    def lab(LWdn, SZA, coef: Coef):
        return qcr.QC5(LWdn, coef)

    def calc_lim(self, df, coef: Coef):
        return gen_calc_lim(self, df, coef)


class QC10:

    def __init__(self):
        self.name = 'QC10'
        self.varx = 'temperature'
        self.vary = 'downward_avg'
        self.unitx = '°K'
        self.unity = 'W.m-2'
        self.coefficients = {'level_1_min': 'C11', 'level_2_min': 'D11', 'level_1': 'C12', 'level_2': 'D12'}
        self.coef_range = [0.0, 10.0]
        self.coef_range_min = [0.60, 1.0]

    @staticmethod
    def f(LWdn, Ta, coef: Coef):
        ''' Return the 2 main variables, the 1rst level limit, the 2nd level limit and the physical limit for a sample'''

        l1_max = qcr.REF.BOLTZMANN * math.pow(Ta + 273.15, 4) + coef.C12
        l2_max = qcr.REF.BOLTZMANN * math.pow(Ta + 273.15, 4) + coef.D12
        l_bsrn_max = 700

        l1_min = coef.C11 * qcr.REF.BOLTZMANN * math.pow(Ta + 274.15, 4)
        l2_min = coef.D11 * qcr.REF.BOLTZMANN * math.pow(Ta + 274.15, 4)
        l_bsrn_min = 40

        return l1_max, l2_max, l_bsrn_max, l1_min, l2_min, l_bsrn_min

    @staticmethod
    def lab(LWdn, Ta, coef: Coef):
        return qcr.QC10(LWdn, Ta + 273.15, coef)

    def calc_lim(self, df, coef: Coef):
        return gen_calc_lim(self, df, coef)
