from pyqcbsrn.automaticQC import generateQCFiles, plotQCFiles
from pyqcbsrn.visualPlot import plotBSRN


def automatic(path):
    generateQCFiles(path)


def visual(path):
    plotBSRN(path)


def plot(path):
    plotQCFiles(path)
