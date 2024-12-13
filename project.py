import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.gridspec import GridSpec
from scipy.interpolate import CubicSpline
import numpy as np


def import_file(file_type):
    try:
        filename = filedialog.askopenfilename(
            title=f"Select {file_type} CSV file", filetypes=[("CSV files", "*.csv")]
        )
    except FileNotFoundError:
        print("File not found. Please select a valid file.")
    except IOError:
        print("Error reading the file. Please try again.")
    else:
        return pd.read_csv(filename)


def bypass_import_files():
    df_sensorgram = pd.read_csv("./sensorgram.csv")
    df_calibration = pd.read_csv("./calibration.csv")
    df_calibration["Average"] = df_calibration.iloc[:, 1:].mean(axis=1)
    return df_sensorgram, df_calibration, df_calibration["Average"]


def convert_fn_RU(df_calibration_avg):
    # df_sensorgram, df_calibration, df = bypass_import_files()
    df = df_calibration_avg
    x = np.array([df.iloc[42:46].mean(), df.iloc[6:10].mean()])
    y = np.array([0, 12000])
    coefficients = np.polyfit(x, y, 1)
    print(f"Coefficients values are: {coefficients}")
    a, b = coefficients
    print(f"The equation for the conversion curve is: y = {a:.4f}x + {b:.4f}")

    # Testing the X values in the table
    plateaus = [
        df.iloc[6:10].mean(),
        df.iloc[12:16].mean(),
        df.iloc[18:22].mean(),
        df.iloc[24:28].mean(),
        df.iloc[30:34].mean(),
        df.iloc[36:40].mean(),
        df.iloc[42:46].mean(),
    ]
    p_function = np.poly1d(coefficients)
    print("These are a few inputs to test the conversion equation:")
    for x_value in plateaus:
        y_value = p_function(x_value)
        print(f"For x = {x_value}, y = {y_value}")

    return p_function


def convert_RU(df_sensorgram, df_calibration):
    # df_sensorgram, df_calibration, df_calibration["Average"] = bypass_import_files()
    # Use this to bypass the button
    df_calibration["Average"] = df_calibration.iloc[:, 1:].mean(axis=1)
    conversion_fn = convert_fn_RU(df_calibration["Average"])
    converted_sensorgram = conversion_fn(
        df_sensorgram.iloc[:, 1:]
    )  # Dropping the first column
    return converted_sensorgram


def reference(converted_sensorgram):
    row_averages = np.mean(converted_sensorgram, axis=1)
    print(f"The number of interval points are: {row_averages.shape[0]}")
    lowest_row_index = np.argmin(row_averages)
    print(f"The index of the row with the lowest mean is: {lowest_row_index}")
    referenced_sensorgram = (
        converted_sensorgram - converted_sensorgram[lowest_row_index]
    )
    return referenced_sensorgram


def process_and_plot(root):
    df_calibration = import_file("Calibration")
    df_sensorgram = import_file("Sensorgram")
    # df_sensorgram, df_calibration, df_calibration["Average"] = bypass_import_files()

    fig = plt.figure(figsize=(16, 9))
    # Define the position of the plotted graphs
    gs = GridSpec(3, 3, figure=fig)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])
    ax5 = fig.add_subplot(gs[2, 0:2])
    ax6 = fig.add_subplot(gs[0:3, 2])

    # Plot calibration
    ax1.set_title("Calibration")
    for column in df_calibration.columns[1:]:
        ax1.plot(df_calibration[column], label=column)
    ax1.set_xlabel("Interval")
    ax1.set_ylabel("ImageJ number")  # What is this number?
    # ax1.legend()

    # Plot sensorgram
    ax2.set_title("Sensorgram")
    for column in df_sensorgram.columns[1:]:
        ax2.plot(df_sensorgram[column], label=column)
    ax2.set_xlabel("Interval")
    ax2.set_ylabel("ImageJ number")  # What is this number?
    # ax2.legend()

    # Plot conversion to refraction units
    converted_sensorgram = convert_RU(df_sensorgram, df_calibration)
    pd_converted_sensorgram = pd.DataFrame(converted_sensorgram)
    ax3.set_title("Converted Sensorgram")
    for column in pd_converted_sensorgram.columns[:]:
        ax3.plot(pd_converted_sensorgram[column], label=column)
    ax3.set_xlabel("Interval")
    ax3.set_ylabel("Refraction Units")
    # ax3.legend()

    # Plot referenced sensorgram
    referenced_sensorgram = reference(converted_sensorgram)
    pd_referenced_sensorgram = pd.DataFrame(referenced_sensorgram)
    ax4.set_title("Referenced Sensorgram")
    for column in pd_referenced_sensorgram.columns[:]:
        ax4.plot(pd_referenced_sensorgram[column], label=column)
    ax4.set_xlabel("Interval")
    ax4.set_ylabel("Normalized Refraction Units")
    ax4.grid(True)
    # ax4.legend()

    # Plot the CubicSpline interpolation
    x_cs = range(len(df_sensorgram))
    y_cs = referenced_sensorgram[:, :]
    x_new_cs = np.linspace(min(x_cs), max(x_cs), 1000)

    for i in range(y_cs.shape[1]):
        cs = CubicSpline(x_cs, y_cs[:, i])
        y_new_cs = cs(x_new_cs)
        ax5.plot(x_new_cs, y_new_cs, label=f"RoI {i+1}")

    ax5.set_title("CubicSplined Referenced Sensorgram")
    # for column in pd_referenced_sensorgram.columns[1:]:
    #     ax5.plot(pd_referenced_sensorgram[column], label=column)
    ax5.set_xlabel("Interval")
    ax5.set_ylabel("Normalized Refraction Units")
    ax5.grid(True)
    # ax5.legend(ncol=4, loc='upper left') # , bbox_to_anchor=(1,1)

    # External legend
    ax6.axis("off")
    handles, labels = ax5.get_legend_handles_labels()
    ax6.legend(handles, labels, ncol=3, loc="center")

    # Plot in the canvas
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    canvas.draw()


def main():
    root = tk.Tk()
    root.configure(width=1920, height=1080)
    root.title("Data Analysis")

    process_button = tk.Button(
        root, text="Process and Plot", command=lambda: process_and_plot(root)
    )
    process_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    # process_and_plot(root) # Use this to bypass the button
    root.mainloop()


if __name__ == "__main__":
    main()
