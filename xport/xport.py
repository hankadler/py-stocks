#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Imports and exports collected data.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


import multiprocessing as mp
import os

import pandas as pd
from pandas import ExcelWriter

import config


EXTENSIONS = ['csv', 'ods', 'txt', 'xlsx', 'pkl']


def export(data_dict: dict, dir: str = config.DATA, ext: str = 'txt'):
    args = []

    for symbol, data in data_dict.items():
        args.append((data, dir, symbol, ext))

    with mp.Pool() as pool:
        pool.starmap(_export, args)


def _export(data: pd.DataFrame, dir:str, fname: str, ext='txt'):
    """
    Writes data `fname`.`ext`.

    Parameters:
        dir (str): Directory of file to export.
        fname (str): Name of file to export, without extension.
        ext (str): `fname` extension. Determines file type. See
        `EXTENSIONS`.
    """
    if not os.path.isdir(dir):
        os.mkdir(dir)

    pathout = f'{dir}/{fname}.{ext}'

    if ext == 'csv':
        data.to_csv(path_or_buf=pathout)
    elif ext == 'pkl':
        data.to_pickle(pathout)
    elif ext == 'txt':
        with open(pathout, 'w') as fh:
            data.to_string(fh)
    elif ext == 'xlsx':
        writer = ExcelWriter(path=pathout)
        data.to_excel(excel_writer=writer, sheet_name='RSI')
        writer.save()

    print(f"Data exported to '{pathout}'.")


if __name__ == '__main__':
    pass
