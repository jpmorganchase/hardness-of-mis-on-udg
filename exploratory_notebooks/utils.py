###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
import pandas as pd
import numpy as np
from matplotlib.ticker import FixedLocator, FuncFormatter, MaxNLocator
import warnings

DICT_RC_PARAM = {
    "font.size": 20,
    "text.usetex": True,
    "font.family": "serif",
    "mathtext.fontset": "dejavuserif",
    "savefig.bbox": "tight",
    "text.latex.preamble": r"\usepackage{amsfonts}",
}


def get_data_frames_cplex(L_range=range(7, 36, 2), d=0.8):
    df = get_cplex_data(d)
    data_frames = dict()
    for L in L_range:
        df_temp = get_degeneracy_data(L, d)
        df_L = df[df["L"] == L].set_index("Seed")
        df_temp["cplex_process_time"] = df_L["Process TTO"]
        df_temp["cplex_TTS_process_time"] = df_L["Process TTS"]
        data_frames[L] = df_temp
    return data_frames


def get_cplex_data(d=0.8):
    base_path = "../generator/data/cplex/"
    df = pd.read_csv(base_path + f"run_time_d{d}_UDG_8vCPU.csv")
    return df


def get_degeneracy_data(L, d=0.8):
    df = (
        pd.read_csv(f"../generator/data/degeneracy/L{L}_d{d}.txt", sep=" ")
        .set_index("seed")
        .sort_index()
    )
    # use astype float as certain number goes over int64
    df["D_(MIS-1)"] = df["D_(MIS-1)"].astype(float)
    df["D_MIS"] = df["D_MIS"].astype(float)
    df["HP"] = df["D_(MIS-1)"].astype(float) / (df["MIS"] * df["D_MIS"].astype(float))
    df["deg_density"] = np.log(df["D_MIS"]) / df["N"]
    return df


def log_wrapper_for_logged_data(ax, x_axis=False, y_axis=True, base=10):
    """
    Trick to have boxplot with log data but have a nice log tickers and minor ticks
    ax: matplotlib axes
    x_axis: bool apply to x axis
    y_axis: bool apply to y axis
    base: base of exponant
    force_int: bool to force the selected axis to have integer tickers
    """

    def ticker_log_formatter(base):
        def sub_func(x, base):
            assert int(x) == x
            return "$" + str(base) + "^{" + str(int(x)) + "}$"

        return FuncFormatter(lambda x, pos=None: sub_func(x, base))

    def get_log_minor_tickers(x_min, x_max):
        x = np.arange(np.floor(x_min), np.ceil(x_max) + 1)
        tickers = []
        for base_x in x:
            tickers += list(base_x + np.log10(np.arange(2, 10)))
        return tickers

    fmt = ticker_log_formatter(base)
    if x_axis:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, min_n_ticks=1))
        x_min, x_max = ax.get_xlim()
        if len(ax.xaxis.get_major_ticks()) < 2:
            warnings.warn(
                "Only one major tick is shown, you can use ax.get_xlim() and ax.set_xlim(xmin, xmax) beforehand to resolve this"
            )
        minor_locator = FixedLocator(get_log_minor_tickers(x_min, x_max))
        ax.xaxis.set(major_formatter=fmt, minor_locator=minor_locator)
    if y_axis:
        ax.yaxis.set_major_locator(MaxNLocator(integer=True, min_n_ticks=1))
        y_min, y_max = ax.get_ylim()
        if len(ax.yaxis.get_major_ticks()) < 2:
            warnings.warn(
                "Only one major tick is shown, you can use ax.get_ylim() and ax.set_ylim(ymin, ymax) beforehand to resolve this"
            )
        minor_locator = FixedLocator(get_log_minor_tickers(y_min, y_max))
        ax.yaxis.set(major_formatter=fmt, minor_locator=minor_locator)
    return ax
