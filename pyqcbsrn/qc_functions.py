"""
Module that provides the QC class with their assiocated functions and labeling
"""


# Imports required
import math
import numpy as np

# Physics variables


class ref:
    """BSRN Various quantities related to measurements"""
    Tsnw = None  # temperature limit for albedo limit test, temp at which "snow" limit is used
    SOLAR_CONSTANT = 1368  # solar constant at mean Earth-Sun distance uses by QCRad in W.m-2
    BOLTZMANN = 5.67e-8  # Stephan-Boltzman constant = 5.67 x 10 -8 Wm -2 K -4


"""
Flag Value: Related to Type test:
5-6 Global Physical Limits (PP)
3-4 User configurable (UC2) 2nd level tests, also LW Tc and Td tests
1-2 User configurable (UC1) 1st level tests and non-definitive tests
0   No test failures
-1  Missing data or test not possible
"""


''' *********** QC1-QC6 (GSW, Diffuse SW, Direct SW, SWup, LWdn and LWup basic limits tests) *********** '''

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

    def f(self, SZA, GSW, coefs):
        ''' Return the 2 main variables, the 1rst level limit, the 2nd level limit and the physical limit for a sample'''

        l1 = ref.SOLAR_CONSTANT * coefs['BSRN']['C1'] * math.pow(math.cos(math.radians(SZA)), 1.2) + 50
        l2 = ref.SOLAR_CONSTANT * coefs['BSRN']['D1'] * math.pow(math.cos(math.radians(SZA)), 1.2) + 55
        l_bsrn = ref.SOLAR_CONSTANT * 1.5 * math.pow(math.cos(math.radians(SZA)), 1.2) + 100

        return l1, l2, l_bsrn

    def lab(self, SZA, GSW, coefs):
        """GSW [basic limits tests]"""
        if GSW is not None:
            if (GSW < -4):
                return 5
            if (GSW < -2):
                return 3
            if SZA >= 0 and SZA <= 90:  # cannot have float exponent of negative value
                if(GSW > (ref.SOLAR_CONSTANT * 1.5 * math.pow(math.cos(math.radians(SZA)), 1.2)) + 100):
                    return 6
                if(GSW > (ref.SOLAR_CONSTANT * coefs['BSRN']['D1'] * math.pow(math.cos(math.radians(SZA)), 1.2)) + 55):
                    return 4
                if(GSW > (ref.SOLAR_CONSTANT * coefs['BSRN']['C1'] * math.pow(math.cos(math.radians(SZA)), 1.2)) + 50):
                    return 2
            else:
                return -1
        else:
            return -1
        return 0

    def calc_lim(self, df, coefs):
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

                l1, l2, l_bsrn, l1_min, l2_min, l_bsrn_min = self.f(VAL1, VAL2, coefs)

                lim_l1_min.append(l1_min)
                lim_l2_min.append(l2_min)
                lim_bsrn_min.append(l_bsrn_min)

            else:

                l1, l2, l_bsrn = self.f(VAL1, VAL2, coefs)

            label = self.lab(VAL1, VAL2, coefs)

            lim_l1.append(l1)
            lim_l2.append(l2)
            lim_bsrn.append(l_bsrn)
            labels.append(label)

        return(lim_l1, lim_l2, lim_bsrn, labels)


class QC2:

    def __init__(self):
        self.name = 'QC2'
        self.varx = 'SZA'
        self.vary = 'diffuse_avg'
        self.unitx = 'SZA'
        self.unity = 'W.m-2'
        self.coefficients = {'level_1': 'C2', 'level_2': 'D2'}
        self.coef_range = [0.0, 1.0]

    def f(self, SZA, Dif, coefs):
        ''' Return the 2 main variables, the 1rst level limit, the 2nd level limit and the physical limit for a sample'''

        l1 = ref.SOLAR_CONSTANT * coefs['BSRN']['C2'] * math.pow(math.cos(math.radians(SZA)), 1.2) + 30
        l2 = ref.SOLAR_CONSTANT * coefs['BSRN']['D2'] * math.pow(math.cos(math.radians(SZA)), 1.2) + 35
        l_bsrn = ref.SOLAR_CONSTANT * 0.95 * math.pow(math.cos(math.radians(SZA)), 1.2) + 50

        return l1, l2, l_bsrn

    def lab(self, SZA, Dif, coefs):
        """Diffuse SW [basic limits tests]"""
        if Dif is not None:
            if (Dif < -4):
                return 5
            if(Dif < -2):
                return 3
            if SZA >= 0 and SZA <= 90:  # cannot have float exponent of negative value
                if(Dif > (ref.SOLAR_CONSTANT * 0.95 * math.pow(math.cos(math.radians(SZA)), 1.2)) + 50):
                    return 6
                if(Dif > (ref.SOLAR_CONSTANT * coefs['BSRN']['D2'] * math.pow(math.cos(math.radians(SZA)), 1.2)) + 35):
                    return 4
                if(Dif > (ref.SOLAR_CONSTANT * coefs['BSRN']['C2'] * math.pow(math.cos(math.radians(SZA)), 1.2)) + 30):
                    return 2
            else:
                return -1
        else:
            return -1
        return 0

    def calc_lim(self, df, coefs):
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

                l1, l2, l_bsrn, l1_min, l2_min, l_bsrn_min = self.f(VAL1, VAL2, coefs)

                lim_l1_min.append(l1_min)
                lim_l2_min.append(l2_min)
                lim_bsrn_min.append(l_bsrn_min)

            else:

                l1, l2, l_bsrn = self.f(VAL1, VAL2, coefs)

            label = self.lab(VAL1, VAL2, coefs)

            lim_l1.append(l1)
            lim_l2.append(l2)
            lim_bsrn.append(l_bsrn)
            labels.append(label)

        return(lim_l1, lim_l2, lim_bsrn, labels)


class QC3:

    def __init__(self):
        self.name = 'QC3'
        self.varx = 'SZA'
        self.vary = 'direct_avg'
        self.unitx = 'SZA'
        self.unity = 'W.m-2'
        self.coefficients = {'level_1': 'C3', 'level_2': 'D3'}
        self.coef_range = [0.0, 1.0]

    def f(self, SZA, DirN, coefs):
        ''' Return the 2 main variables, the 1rst level limit, the 2nd level limit and the physical limit for a sample'''

        l1 = ref.SOLAR_CONSTANT * coefs['BSRN']['C3'] * math.pow(math.cos(math.radians(SZA)), 0.2) + 10
        l2 = ref.SOLAR_CONSTANT * coefs['BSRN']['D3'] * math.pow(math.cos(math.radians(SZA)), 0.2) + 15
        l_bsrn = ref.SOLAR_CONSTANT

        return l1, l2, l_bsrn

    def lab(self, SZA, DirN, coefs):
        """Direct Normal SW  [basic limits tests]"""
        if DirN is not None:
            if (DirN < -4):
                return 5
            if(DirN < -2):
                return 3
            if (DirN > ref.SOLAR_CONSTANT):
                return 6
            if SZA >= 0 and SZA <= 90:  # cannot have float exponent of negative value
                if(DirN > (ref.SOLAR_CONSTANT * coefs['BSRN']['D3'] * math.pow(math.cos(math.radians(SZA)), 0.2)) + 15):
                    return 4
                if(DirN > (ref.SOLAR_CONSTANT * coefs['BSRN']['C3'] * math.pow(math.cos(math.radians(SZA)), 0.2)) + 10):
                    return 2
            else:
                return -1
        else:
            return -1
        return 0

    def calc_lim(self, df, coefs):
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

                l1, l2, l_bsrn, l1_min, l2_min, l_bsrn_min = self.f(VAL1, VAL2, coefs)

                lim_l1_min.append(l1_min)
                lim_l2_min.append(l2_min)
                lim_bsrn_min.append(l_bsrn_min)

            else:

                l1, l2, l_bsrn = self.f(VAL1, VAL2, coefs)

            label = self.lab(VAL1, VAL2, coefs)

            lim_l1.append(l1)
            lim_l2.append(l2)
            lim_bsrn.append(l_bsrn)
            labels.append(label)

        return(lim_l1, lim_l2, lim_bsrn, labels)


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

    def f(self, SZA, LWdn, coefs):
        ''' Return the 2 main variables, the 1rst level limit, the 2nd level limit and the physical limit for a sample'''

        l1_max = coefs['BSRN']['C6']
        l2_max = coefs['BSRN']['D6']
        l_bsrn_max = 700

        l1_min = coefs['BSRN']['C5']
        l2_min = coefs['BSRN']['D5']
        l_bsrn_min = 40

        return l1_max, l2_max, l_bsrn_max, l1_min, l2_min, l_bsrn_min

    def lab(self, Ta, LWdn, coefs):
        """LWdn [basic limits tests]"""
        if LWdn is not None:
            if (LWdn > 700):
                return 6
            if (LWdn < 40):
                return 5
            if (LWdn > coefs['BSRN']['D6']):
                return 4
            if (LWdn < coefs['BSRN']['D5']):
                return 3
            if (LWdn > coefs['BSRN']['C6']):
                return 2
            if (LWdn < coefs['BSRN']['C5']):
                return 1
        else:
            return -1
        return 0

    def calc_lim(self, df, coefs):
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

            l1, l2, l_bsrn, l1_min, l2_min, l_bsrn_min = self.f(VAL1, VAL2, coefs)

            lim_l1_min.append(l1_min)
            lim_l2_min.append(l2_min)
            lim_bsrn_min.append(l_bsrn_min)

            label = self.lab(VAL1, VAL2, coefs)

            lim_l1.append(l1)
            lim_l2.append(l2)
            lim_bsrn.append(l_bsrn)
            labels.append(label)

        return(lim_l1, lim_l2, lim_bsrn, labels)


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

    def f(self, Ta, LWdn, coefs):
        ''' Return the 2 main variables, the 1rst level limit, the 2nd level limit and the physical limit for a sample'''

        l1_max = ref.BOLTZMANN * math.pow(Ta + 273.15, 4) + coefs['BSRN']['C12']
        l2_max = ref.BOLTZMANN * math.pow(Ta + 273.15, 4) + coefs['BSRN']['D12']
        l_bsrn_max = 700

        l1_min = coefs['BSRN']['C11'] * ref.BOLTZMANN * math.pow(Ta + 274.15, 4)
        l2_min = coefs['BSRN']['D11'] * ref.BOLTZMANN * math.pow(Ta + 274.15, 4)
        l_bsrn_min = 40

        return l1_max, l2_max, l_bsrn_max, l1_min, l2_min, l_bsrn_min

    def lab(self, Ta, LWdn, coefs):
        """LWdn to Ta test"""
        if all(v is not None for v in [LWdn, Ta]):
            if QC19(Ta) == 0:
                if (LWdn > (ref.BOLTZMANN * math.pow(Ta, 4) + coefs['BSRN']['D12'])):
                    return 4
                if (LWdn < (coefs['BSRN']['D11'] * ref.BOLTZMANN * math.pow(Ta, 4))):
                    return 3
                if (LWdn > (ref.BOLTZMANN * math.pow(Ta, 4) + coefs['BSRN']['C12'])):
                    return 2
                if (LWdn < (coefs['BSRN']['C11'] * ref.BOLTZMANN * math.pow(Ta, 4))):
                    return 1
            else:
                return -1
        else:
            return -1
        return 0

    def calc_lim(self, df, coefs):
        """ Computation of the limits and the labels of a dataframe"""

        df = df[['timestamp', self.varx, self.vary]]

        X_val1 = np.array(df[self.varx]) + 273.15
        X_val2 = np.array(df[self.vary])

        lim_l1 = []
        lim_l2 = []
        lim_bsrn = []

        lim_l1_min = []
        lim_l2_min = []
        lim_bsrn_min = []

        labels = []

        for VAL1, VAL2 in zip(X_val1, X_val2):

            l1, l2, l_bsrn, l1_min, l2_min, l_bsrn_min = self.f(VAL1, VAL2, coefs)

            lim_l1_min.append(l1_min)
            lim_l2_min.append(l2_min)
            lim_bsrn_min.append(l_bsrn_min)

            label = self.lab(VAL1, VAL2, coefs)

            lim_l1.append(l1)
            lim_l2.append(l2)
            lim_bsrn.append(l_bsrn)
            labels.append(label)

        return(lim_l1, lim_l2, lim_bsrn, labels)

# -------------------------------------------------------------------------------------------


def QC19(Ta):
    """Ta testing"""
    if Ta is not None:
        if Ta > 350 or Ta < 170:
            return 1
    else:
        return -1
    return 0
