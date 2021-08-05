import math
from pybsrnqc.config import Coef

default_coef = Coef()


class REF:
    """BSRN Various quantities related to measurements"""
    TSWN = None  # temperature limit for albedo limit test, temp at which "snow" limit is used
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


def QC1(GSW, SZA, coef: Coef = default_coef):
    """GSW [basic limits tests]"""
    if GSW is not None:
        if (GSW < -4):
            return 5
        if (GSW < -2):
            return 3
        if SZA >= 0 and SZA <= 90: # cannot have float exponent of negative value
            if(GSW > (REF.SOLAR_CONSTANT * 1.5 * math.pow(math.cos(math.radians(SZA)), 1.2)) + 100):
                return 6
            if(GSW > (REF.SOLAR_CONSTANT * coef.D1 * math.pow(math.cos(math.radians(SZA)), 1.2)) + 55):
                return 4
            if(GSW > (REF.SOLAR_CONSTANT * coef.C1 * math.pow(math.cos(math.radians(SZA)), 1.2)) + 50):
                return 2
        else:
            return -1
    else:
        return -1
    return 0


def QC2(Dif, SZA, coef: Coef = default_coef):
    """Diffuse SW [basic limits tests]"""
    if Dif is not None:
        if (Dif < -4):
            return 5
        if(Dif < -2):
            return 3
        if SZA >= 0 and SZA <= 90: # cannot have float exponent of negative value
            if(Dif > (REF.SOLAR_CONSTANT * 0.95 * math.pow(math.cos(math.radians(SZA)), 1.2)) + 50):
                return 6
            if(Dif > (REF.SOLAR_CONSTANT * coef.D2 * math.pow(math.cos(math.radians(SZA)), 1.2)) + 35):
                return 4
            if(Dif > (REF.SOLAR_CONSTANT * coef.C2 * math.pow(math.cos(math.radians(SZA)), 1.2)) + 30):
                return 2
        else:
            return -1
    else:
        return -1
    return 0


def QC3(DirN, SZA, coef: Coef = default_coef):
    """Direct Normal SW  [basic limits tests]"""
    if DirN is not None:
        if (DirN < -4):
            return 5
        if(DirN < -2):
            return 3
        if (DirN > REF.SOLAR_CONSTANT):
            return 6
        if SZA >= 0 and SZA <= 90: # cannot have float exponent of negative value
            if(DirN > (REF.SOLAR_CONSTANT * coef.D3 * math.pow(math.cos(math.radians(SZA)), 0.2)) + 15):
                return 4
            if(DirN > (REF.SOLAR_CONSTANT * coef.C3 * math.pow(math.cos(math.radians(SZA)), 0.2)) + 10):
                return 2
        else:
            return -1
    else:
        return -1
    return 0


def QC4(SWup, SZA, coef: Coef = default_coef):
    """SWup [basic limits tests]"""
    if SWup is not None:
        if (SWup < -4):
            return 5
        if(SWup < -2):
            return 3
        if SZA >= 0 and SZA <= 90: # cannot have float exponent of negative value
            if (SWup > (REF.SOLAR_CONSTANT * 1.2 * math.pow(math.cos(math.radians(SZA)), 1.2)) + 50):
                return 6
            if(SWup > (REF.SOLAR_CONSTANT * coef.D4 * math.pow(math.cos(math.radians(SZA)), 1.2)) + 55):
                return 4
            if(SWup > (REF.SOLAR_CONSTANT * coef.C4 * math.pow(math.cos(math.radians(SZA)), 1.2)) + 50):
                return 2
        else:
            return -1
    else:
        return -1
    return 0


def QC5(LWdn, coef: Coef = default_coef):
    """LWdn [basic limits tests]"""
    if LWdn is not None:
        if (LWdn > 700):
            return 6
        if (LWdn < 40):
            return 5
        if (LWdn > coef.D6):
            return 4
        if (LWdn < coef.D5):
            return 3
        if (LWdn > coef.C6):
            return 2
        if (LWdn < coef.C5):
            return 1
    else:
        return -1
    return 0


def QC6(LWup, coef: Coef = default_coef):
    """LWup [basic limits tests]"""
    if LWup is not None:
        if (LWup > 900):
            return 6
        if (LWup < 40):
            return 5
        if (LWup > coef.D7):
            return 4
        if (LWup < coef.D8):
            return 3
        if (LWup > coef.C7):
            return 2
        if (LWup < coef.C8):
            return 1
    else:
        return -1
    return 0


def QC7(GSW, Dif, DirN, SZA):
    """GSW/Sum test [non-definitive]"""
    if all(v is not None for v in [GSW, Dif, DirN, SZA]):
        if SZA < 93:
            SumSW = Dif + (DirN * math.cos(math.radians(SZA)) )
            if SumSW > 50:
                if (SZA > 75 and SZA < 93 and ( ((GSW/SumSW)<0.85) or ((GSW/SumSW)>1.15) )):
                    return 2
                if (SZA < 75 and ( ((GSW/SumSW)<0.92) or ((GSW/SumSW)>1.08) )):
                    return 1
            else:
                return -1
        else:
            return -1
    else:
        return -1
    return 0


def QC8(Dif, GSW, SZA):
    """Dif/GSW test [non-definitive]"""
    if all(v is not None for v in [GSW, Dif, SZA]):
        if SZA >= 0 and SZA <= 90: # test between 0 and 90 degrees because we cannot have float exponent of negative value
            if GSW > 50:
                if (SZA > 75 and SZA < 93 and (Dif/GSW) > 1.10):
                    return 2
                if (SZA < 75 and (Dif/GSW) > 1.05):
                    return 1
            else:
                return -1
        else:
            return -1
    else:
        return -1
    return 0


def QC9(SWup, Dif, DirN, GSW, Ta, SZA, coef: Coef = default_coef):
    """SWup vs Sum SW test"""
    if all(v is not None for v in [GSW, SWup, Ta]):
        if all(v is not None for v in [Dif, DirN]):
            SumSW = Dif + (DirN * math.cos(math.radians(SZA)) )
            if (SumSW > 50 and GSW > 50 and SWup > SumSW and SWup > GSW):
                return 5
            if (SumSW > 50 and SWup > SumSW):
                return 3
            if ( Ta < REF.TSWN and (SumSW > 50 or GSW > 50) and SWup > (coef.C10*SumSW+25)):
                return 2
            if ( Ta >= REF.TSWN and (SumSW > 50 or GSW > 50) and SWup > (coef.C9*SumSW+25)):
                return 1
        elif (GSW > 50 and SWup > GSW):
                return 4
    else:
        return -1
    return 0


def QC10(LWdn, Ta, coef: Coef = default_coef):
    """LWdn to Ta test"""
    if all(v is not None for v in [LWdn, Ta]):
        if QC19(Ta) == 0:
            if (LWdn > (REF.BOLTZMANN * math.pow(Ta, 4) + coef.D12)):
                return 4
            if (LWdn < (coef.D11 * REF.BOLTZMANN * math.pow(Ta, 4))):
                return 3
            if (LWdn > (REF.BOLTZMANN * math.pow(Ta, 4) + coef.C12)):
                return 2
            if (LWdn < (coef.C11 * REF.BOLTZMANN * math.pow(Ta, 4))):
                return 1
        else:
            return -1
    else:
        return -1
    return 0


def QC11(LWup, Ta, coef: Coef = default_coef):
    """LWup to Ta test"""
    if all(v is not None for v in [LWup, Ta]):
        if QC19(Ta) == 0:
            if (LWup > (REF.BOLTZMANN * math.pow(Ta+coef.D14, 4))):
                return 4
            if (LWup < (REF.BOLTZMANN * math.pow(Ta-coef.D13, 4))):
                return 3
            if (LWup > (REF.BOLTZMANN * math.pow(Ta+coef.C14, 4))):
                return 2
            if (LWup < (REF.BOLTZMANN * math.pow(Ta-coef.C13, 4))):
                return 1
        else:
            return -1
    else:
        return -1
    return 0


def QC12(LWdn, LWup, coef: Coef = default_coef):
    """LWdn to LWup test"""
    if all(v is not None for v in [LWdn, LWup]):
        if LWdn > LWup + coef.D16:
            return 4
        if LWdn < LWup - coef.D15:
            return 3
        if LWdn > LWup + coef.C16:
            return 2
        if LWdn < LWup - coef.C15:
            return 1
    else:
        return -1
    return 0


def QC13(Tc, Ta, coef: Coef = default_coef):
    """LWdn Tc vs Ta"""
    if all(v is not None for v in [Tc, Ta]):
        if Tc > Ta + coef.C17D:
            return 4
        if Tc < Ta - coef.C17D:
            return 3
    else:
        return -1
    return 0


def QC14(Td, Ta, coef: Coef = default_coef):
    """LWdn Td vs Ta"""
    if all(v is not None for v in [Td, Ta]):
        if Td > Ta + coef.C17D:
            return 4
        if Td < Ta - coef.C17D:
            return 3
    else:
        return -1
    return 0


def QC15(Tc, Ta):
    """LWup Tc vs Ta"""
    # Do not have Tc from LWup
    return -1


def QC16(Td, Ta):
    """LWup Td vs Ta"""
    # Do not have Td from LWup
    return -1


def QC17(Tc, Td, coef: Coef = default_coef):
    """LWdn Tc vs Td"""
    if all(v is not None for v in [Tc, Td]):
        if (Tc - Td) > coef.C19:
            return 4
        if (Tc - Td) < coef.C18:
            return 3
    else:
        return -1
    return 0


def QC18(Tc, Td):
    """LWup Tc vs Td"""
    # Do not have Tc and Td from LWup
    return -1


def QC19(Ta):
    """Ta testing"""
    if Ta is not None:
        if Ta > 350 or Ta < 170:
            return 1
    else:
        return -1
    return 0
