#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks xport module.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


import os

import pandas as pd

from collector import Collector
import xport


TEST_DIR = os.path.dirname(__file__)

_collector = None
_symbols = []
_prices = None


def set_input():
    global _collector, _symbols, _prices
    _collector = Collector()
    _symbols = ['AAPL', 'MSFT']
    _prices = _collector.get_prices(_symbols)


def check_export_db():
    xport.export(_prices, dir=TEST_DIR, ext='db')


def check_export_csv():
    xport.export(_prices, dir=TEST_DIR, ext='csv')


def check_export_pkl():
    xport.export(_prices, dir=TEST_DIR, ext='pkl')
    data = pd.read_pickle('AAPL.pkl')  # TODO: make arg parametric...
    print(data)


def check_export_txt():
    xport.export(_prices, dir=TEST_DIR, ext='txt')


def check_export_xlsx():
    xport.export(_prices, dir=TEST_DIR, ext='xlsx')


if __name__ == '__main__':
    set_input()
    # check_export_db()
    # check_export_csv()
    check_export_pkl()
    # check_export_txt()
    # check_export_xlsx()
