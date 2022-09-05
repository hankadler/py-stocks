#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Functions for plotting.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


import datetime as dt
import math
import numbers
import os

import matplotlib.pyplot as plt

import config


MAX_LIMIT = 20
LAYOUTS = {
    1: (1, 1), 2: (1, 2), 3: (1, 3), 4: (2, 2), 5: (2, 3), 6: (2, 3),
    7: (2, 4), 8: (2, 4), 9: (3, 3), 10: (2, 5), 11: (3, 4), 12: (3, 4),
    13: (4, 4), 14: (4, 4), 15: (4, 4), 16: (4, 4), 17: (4, 5), 18: (4, 5),
    19: (4, 5), 20: (4, 5)}
ITEMS = ['Date', 'Time', 'Price', 'Volume', 'RSI', 'Min', 'Max']


def plot_density(df_dict, ylabel, q_low = 0.005, q_avg=0.5,
                 show=True, watchlist=None):
    """Generates a subplot for each pd.DataFrame in `df_dict`.

    Parameters:
        df_dict (dict): Keys=symbols (str), values=data (pd.DataFrame).
        ylabel (str): Name of data column to plot.
        q_low (float): Quartile to regard as low.
        q_avg (float): Quartile to regard as average.
        show (bool): Flag for showing plot.
        watchlist (str): Symbols group.

    Returns:
        tuple: Figure and axes.

    Raises:
        Exception: Size of `df_dict` exceeds the max. allowable subplots.
        ValueError: Requested `df_col` is not available.
    """
    if not df_dict:
        return

    if len(df_dict) > MAX_LIMIT:
        raise Exception(
            f'len(df_dict)={len(df_dict)} > MAX_LIMIT' f'={MAX_LIMIT}!'
        )

    if ylabel not in ITEMS:
        raise ValueError(
            f'Invalid ylabel={ylabel}. Valid values are: {ITEMS}'
        )

    subplot_count = len(df_dict)
    nrows, ncols = LAYOUTS[subplot_count]
    fig, axs = plt.subplots(nrows, ncols)
    time_ = dt.datetime.now().strftime('%I:%M %p')
    if watchlist is not None:
        suptitle = f'{watchlist} {ylabel} @ {time_}'
    else:
        suptitle = ylabel
    fig.suptitle(suptitle, size=36, weight='bold' )
    fig.canvas.set_window_title(f'{ylabel} Density')
    plot_indexes = []

    for row in range(nrows):
        for col in range(ncols):
            plot_indexes.append((row, col))

    i = 0
    for symbol, data in df_dict.items():
        x = data[ylabel]

        try:
            x_low = math.floor(x.quantile(q_low))
            x_avg = math.floor(x.quantile(q_avg))
            x_now = x.iloc[-1]
            x_min = x_avg - 3 * x.std()
            x_max = x_avg + 3 * x.std()
        except ValueError:
            continue

        row, col = plot_indexes[i]
        if subplot_count == 1:
            ax = x.plot.kde(ax=axs, title=symbol)
        elif subplot_count == 2:
            ax = x.plot.kde(ax=axs[i], title=symbol)
        else:
            ax = x.plot.kde(ax=axs[row, col], title=symbol)

        ax.set_xlabel(ylabel)
        ax.set_xlim(left=math.floor(x_min), right=math.ceil(x_max))
        ax.set_ylim(bottom=0)
        y_lims = ax.get_ylim()
        y_mid = sum(y_lims) / len(y_lims)
        y_step = y_mid / 25
        ax.axvline(x=x_low, color='green', ls='--', lw=1)
        ax.text(
            x_low * 1.005, y_lims[0] + y_step, f'{x_low}', color='green',
            rotation=90
        )
        ax.axvline(x=x_avg, color='red', ls='--', lw=1)
        ax.text(
            x_avg * 1.005, y_lims[0] + y_step, f'{x_avg}', color='red',
            rotation=90
        )
        ax.axvline(x=x_now, lw=0.5, color='black')
        ax.text(x_now * 1.005, y_mid, f'{x_now}', rotation=90)

        i += 1

    plt.subplots_adjust(wspace=0.50, hspace=0.50)

    if show:
        plt.get_current_fig_manager().window.showMaximized()
        plt.ion()
        plt.show()

    return (fig, axs)


def save_density(df_dict, df_col, q_low = 0.005, q_avg=0.5, show=False,
                 watchlist=None, dir=config.DATA):
    """Saves the density figure as an SVG.

    Parameters:
        df_dict (dict): Keys=symbols (str), values=data (pd.DataFrame).
        df_col (str): Name of pd.DataFrame column to plot.
        q_low (float): Quartile to regard as low.
        q_avg (float): Quartile to regard as average.
        show (bool): Flag for showing plot.

    Returns:
        tuple: Figure and axes.

    Raises:
        Exception: Size of `df_dict` exceeds the max. allowable subplots.
        ValueError: Requested `ylabel` is not available.
    """
    if not df_dict:
        return

    fig = plot_density(df_dict, df_col, q_low, q_avg, show)[0]
    fig.set_size_inches(20, 10)
    date = dt.datetime.now().strftime('%Y-%m-%d')
    # fname = f'{dir}/{ylabel}-kde-{date}.svg'
    if watchlist is not None:
        fname = f'{dir}/{watchlist}-{df_col}-kde.svg'
    else:
        fname = f'{dir}/{df_col}-kde.svg'

    try:
        os.remove(fname)
    except:
        pass

    fig.savefig(fname=fname, transparent=True, dpi=100)

    if show:
        plt.get_current_fig_manager().window.showMaximized()
        plt.show()


def plot_scatter(df_dict, xlabel, ylabel, show=True):
    """Generates a scatter plot for each pd.DataFrame in `df_dict`.

    Parameters:
        df_dict (dict): Keys=symbols (str), values=data (pd.DataFrame).
        xlabel (str): Name of pd.DataFrame column to plot in x.
        ylabel (str): Name of pd.DataFrame column to plot in y.
        show (bool): Flag for showing plot.

    Returns:
        tuple: Figure and axes.

    Raises:
        Exception: Size of `df_dict` exceeds the max. allowable subplots.
        ValueError: Requested `ylabel` is not available.
    """
    if not df_dict:
        return

    if len(df_dict) > MAX_LIMIT:
        raise Exception(
            f'len(df_dict)={len(df_dict)} > MAX_LIMIT' f'={MAX_LIMIT}!'
        )

    if xlabel not in ITEMS:
        raise ValueError(
            f'Invalid xlabel={xlabel}. Valid values are: {ITEMS}'
        )

    if ylabel not in ITEMS:
        raise ValueError(
            f'Invalid ylabel={ylabel}. Valid values are: {ITEMS}'
        )

    subplot_count = len(df_dict)
    nrows, ncols = LAYOUTS[subplot_count]
    fig, axs = plt.subplots(nrows, ncols)
    fig.canvas.set_window_title(f'{ylabel} Scatter')
    plot_indexes = []

    for row in range(nrows):
        for col in range(ncols):
            plot_indexes.append((row, col))

    i = 0
    for symbol, data in df_dict.items():
        x = data[xlabel]
        if not isinstance(x.iloc[-1], numbers.Number):
            x = x.astype(str)
        y = data[ylabel]

        row, col = plot_indexes[i]
        if subplot_count == 1:
            axs.plot(x, y)
            ax = axs
        elif subplot_count == 2:
            axs[i].plot(x, y)
            ax = axs[i]
        else:
            axs[row, col].plot(x, y)
            ax = axs[row, col]

        ax.set_title(symbol)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(xlabel)

        i += 1

    plt.subplots_adjust(wspace=0.50, hspace=0.25)

    if show:
        plt.get_current_fig_manager().window.showMaximized()
        plt.show()

    return (fig, axs)


def plot_bar(df_dict, xlabel, ylabel, show=True):
    """Generates a bar plot for each pd.DataFrame in `df_dict`.

    Parameters:
        df_dict (dict): Keys=symbols (str), values=data (pd.DataFrame).
        xlabel (str): Name of pd.DataFrame column to plot in x.
        ylabel (str): Name of pd.DataFrame column to plot in y.
        show (bool): Flag for showing plot.

    Returns:
        tuple: Figure and axes.

    Raises:
        Exception: Size of `df_dict` exceeds the max. allowable subplots.
        ValueError: Requested `ylabel` is not available.
    """
    if not df_dict:
        return

    if len(df_dict) > MAX_LIMIT:
        raise Exception(
            f'len(df_dict)={len(df_dict)} > MAX_LIMIT' f'={MAX_LIMIT}!'
        )

    if xlabel not in ITEMS:
        raise ValueError(
            f'Invalid xlabel={xlabel}. Valid values are: {ITEMS}'
        )

    if ylabel not in ITEMS:
        raise ValueError(
            f'Invalid ylabel={ylabel}. Valid values are: {ITEMS}'
        )

    subplot_count = len(df_dict)
    nrows, ncols = LAYOUTS[subplot_count]
    fig, axs = plt.subplots(nrows, ncols)
    fig.canvas.set_window_title(f'{ylabel} Bar')
    plot_indexes = []

    for row in range(nrows):
        for col in range(ncols):
            plot_indexes.append((row, col))

    i = 0
    for symbol, data in df_dict.items():
        x = data[xlabel]
        if not isinstance(x.iloc[-1], numbers.Number):
            x = x.astype(str)
        y = data[ylabel]

        row, col = plot_indexes[i]
        if subplot_count == 1:
            axs.bar(x, y)
            ax = axs
        elif subplot_count == 2:
            axs[i].bar(x, y)
            ax = axs[i]
        else:
            axs[row, col].bar(x, y)
            ax = axs[row, col]

        ax.set_title(symbol)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(xlabel)

        i += 1

    plt.subplots_adjust(wspace=0.50, hspace=0.25)

    if show:
        plt.get_current_fig_manager().window.showMaximized()
        plt.show()

    return (fig, axs)


if __name__ == '__main__':
    pass
