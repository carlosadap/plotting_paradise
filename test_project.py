from project import bypass_import_files, convert_fn_RU, convert_RU
import pandas as pd
import numpy as np


def test_bypass_import_files():
    df1, df2, df3 = bypass_import_files()
    calibration = pd.read_csv("./calibration.csv")
    calibration["Average"] = calibration.iloc[:, 1:].mean(axis=1)
    assert not df1.empty, "Sensorgram is empty"
    assert not df2.empty, "Calibration is empty"
    assert df3.all() == calibration["Average"].all(), "Didn't find the average"


def test_convert_fn_RU():
    df1, df2, df3 = bypass_import_files()
    x = np.array([20355.22675, 30295.8285])
    y = np.array([0, 12000])
    coefficients = np.polyfit(x, y, 1)
    a, b = coefficients
    p_function = np.poly1d(coefficients)
    assert isinstance(
        convert_fn_RU(df3), np.poly1d
    ), "The object is not an instance of numpy.poly1d"
    assert p_function == convert_fn_RU(df3), "Should give the same results with fixed x"


def test_convert_RU():
    df1, df2, df3 = bypass_import_files()
    assert isinstance(convert_RU(df1, df2), np.ndarray), "Should output an Numpy Array"
    df_calibration = pd.DataFrame([
        [0, 10, 20],
        [0, 30, 40]
    ])
    df_sensorgram = pd.DataFrame([
        [0, 100, 200],
        [0, 150, 250]
    ])
    assert isinstance(convert_RU(df_sensorgram, df_calibration), np.ndarray)
