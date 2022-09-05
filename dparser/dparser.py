#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parses stock data.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


import datetime as dt

import pandas as pd
from scipy.signal import argrelmin, argrelmax


INTERVALS = ['1m', '2m', '1h', '1d']


def filter(data: pd.DataFrame , start_date: str = None, end_date: str = None,
           start_time: str = None, end_time: str = None):
    """Returns data filtered by date and/or time_.

    Parameters:
        data (Dataframe): Data to filter.
        start_date (str): Start date in 'Date' data column.
        end_date (str): End date in 'Date' data column.
        start_time (str): Start time_ in 'Date' data column.
        end_time (str): End time_ in 'Date' data column.

    Returns:
        pd.DataFrame: Filtered data.
    """
    # Converts date and time_ strings to dt.date and dt.time_ objects.
    if start_date is not None:
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date is not None:
        end_date = dt.datetime.strptime(end_date, '%Y-%m-%d').date()
    if start_time is not None:
        start_time = dt.datetime.strptime(start_time, '%I:%M %p').time()
    if end_time is not None:
        end_time = dt.datetime.strptime(end_time, '%I:%M %p').time()

    # Filters data.
    if (start_date is not None) and (end_date is not None):
        mask = (data['Date'] >= start_date) & (data['Date'] <= end_date)
        data = data.loc[mask]
    if (start_time is not None) and (end_time is not None):
        mask = (data['Time'] >= start_time) & (data['Time'] <= end_time)
        data = data.loc[mask]

    return data


def split(data: pd.DataFrame, interval='1d'):
    splitted = []

    if interval == '1d':
        for date in data['Date'].unique():
            splitted.append(data.loc[data['Date'] == date])

    return splitted


def get_local_min(data: pd.DataFrame, col: str, order: int):
    indexes = argrelmin(data[col].values, order=order)[0]
    df = data.iloc[indexes][['Date', 'Time', col]]
    df.reset_index(drop=True, inplace=True)
    # df.rename(columns={col: 'Min'}, inplace=True)
    return df


def get_local_max(data: pd.DataFrame, col: str, order: int):
    indexes = argrelmax(data[col].values, order=order)[0]
    df = data.iloc[indexes][['Date', 'Time', col]]
    df.reset_index(drop=True, inplace=True)
    # df.rename(columns={col: 'Max'}, inplace=True)
    return df


def get_delta(df_1, df_2, col):
    """Returns df_2[col] - df_1[col] pd.DataFrame."""
    if (col == 'Date') or (col == 'Time'):
        dt_1 = pd.to_datetime(
            df_1['Date'].astype(str) + ' ' + df_1['Time'].astype(str)
        )
        dt_2 = pd.to_datetime(
            df_2['Date'].astype(str) + ' ' + df_2['Time'].astype(str)
        )
        delta = (dt_2 - dt_1).dt.total_seconds() / 60
    else:
        delta = df_2[col] - df_1[col]

    return pd.DataFrame({'Delta': delta})
    # return delta


if __name__ == '__main__':
    pass
