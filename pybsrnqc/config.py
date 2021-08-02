import importlib.resources
import json

# Load default conf from package
with importlib.resources.path("pybsrnqc", "qcrad_conf.json") as data_path:
    with open(data_path, 'r') as f:
        loaded_json = json.load(f)


class Station:

    def __init__(self):
        self.LAT = loaded_json['STATION']['LAT']
        self.LON = loaded_json['STATION']['LON']
        self.ALT = loaded_json['STATION']['ALT']
        self.TZ = loaded_json['STATION']['TZ']


class Coef:

    def __init__(self):
        self.C1 = loaded_json['COEF']["C1"]
        self.D1 = loaded_json['COEF']["D1"]
        self.C2 = loaded_json['COEF']["C2"]
        self.D2 = loaded_json['COEF']["D1"]
        self.C3 = loaded_json['COEF']["C3"]
        self.D3 = loaded_json['COEF']["D3"]
        self.C5 = loaded_json['COEF']["C5"]
        self.D5 = loaded_json['COEF']["D5"]
        self.C6 = loaded_json['COEF']["C6"]
        self.D6 = loaded_json['COEF']["D6"]
        self.C11 = loaded_json['COEF']["C11"]
        self.D11 = loaded_json['COEF']["D11"]
        self.C12 = loaded_json['COEF']["C12"]
        self.D12 = loaded_json['COEF']["D12"]
        self.C17D = loaded_json['COEF']["C17D"]
        self.C18 = loaded_json['COEF']["C18"]
        self.C19 = loaded_json['COEF']["C19"]


class Header:

    def __init__(self):
        self.TIMESTAMP_NAME = loaded_json['HEADER']['TIMESTAMP_NAME']
        self.GSW_NAME = loaded_json['HEADER']['GSW_NAME']
        self.DIF_NAME = loaded_json['HEADER']['DIF_NAME']
        self.DIR_NAME = loaded_json['HEADER']['DIR_NAME']
        self.LWDN_NAME = loaded_json['HEADER']['LWDN_NAME']
        self.TA_NAME = loaded_json['HEADER']['TA_NAME']

