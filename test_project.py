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


def test_convest_fn_RU():
    columns = [f"ROI{i}" for i in range(101)]
    np.random.seed(42)
    df = pd.DataFrame(np.random.rand(46, 101), columns=columns)
    df_avg = df.iloc[:, 1:].mean(axis=1)

    x = np.array([df_avg.iloc[42:46].mean(), df_avg.iloc[6:10].mean()])
    y = np.array([0, 12000])
    coefficients = np.polyfit(x, y, 1)
    p_function = np.poly1d(coefficients)
    assert p_function == convert_fn_RU(
        df_avg
    ), "Should return the same conversion function with a random dataframe"


def test_convert_RU():
    df_sensorgram_columns = [f"ROI{i}" for i in range(101)]
    np.random.seed(42)
    df_sensorgram = pd.DataFrame(
        np.random.rand(256, 101), columns=df_sensorgram_columns
    )

    df_calibration_columns = [f"ROI{i}" for i in range(102)]
    df_calibration = pd.DataFrame(
        np.random.rand(46, 102), columns=df_calibration_columns
    )

    df_avg = df_calibration.iloc[:, 1:].mean(axis=1)
    conversion_fn = convert_fn_RU(df_avg)
    converted_sensorgram = conversion_fn(df_sensorgram.iloc[:, 1:])
    assert (
        converted_sensorgram.all() == convert_RU(df_sensorgram, df_calibration).all()
    ), "Should give the same values with a random dataframe"
