import importlib.resources
import json


def load(name_coef, coef, name_coef_min=None, coef_min=None):

    json_lines = []

    with importlib.resources.path("pyqcbsrn", "qcrad_conf.json") as data_path:
        with open(data_path, 'r') as f:
            dic_coefs = json.load(f)

    with importlib.resources.path("pyqcbsrn", "qcrad_conf.json") as data_path:
        with open(data_path, 'w') as open_file:
            open_file.writelines('\n'.join(json_lines))

    if name_coef_min is not None: 
        dic_coefs['BSRN'][name_coef_min] = coef_min

    dic_coefs['BSRN'][name_coef] = coef

    with importlib.resources.path("pyqcbsrn", "qcrad_conf.json") as data_path:
        with open(data_path, 'w') as open_file:
            json.dump(dic_coefs, open_file)