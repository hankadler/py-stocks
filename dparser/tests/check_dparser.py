#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks dparser module.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


import pandas as pd

from collector import Collector
import dparser


def check_filter():
    print('--- check_filter() ---')
    collector = Collector()
    symbol = 'AAPL'
    prices = collector.get_prices([symbol])[symbol]
    subprices = dparser.filter(
        prices, '2021-01-29', '2021-01-29', '9:30 AM', '4:00 PM'
    )
    print(f'prices =')
    print(prices, '\n')
    print(f'filtered =')
    print(subprices, '\n')


def check_split():
    print('--- check_split() ---')
    collector = Collector()
    symbol = 'AAPL'
    prices = collector.get_prices([symbol], period='5d', interval='2m')[symbol]
    result = dparser.split(prices, '1d')
    for r in result:
        print(r)


def check_local_extrema():
    print('=== check_local_extrema() ===')
    collector = Collector()
    symbol = 'AI'
    prices = collector.get_prices([symbol])[symbol]

    print(f'SYMBOL: {symbol}')
    for subprices in dparser.split(prices, interval='1d'):
        min = dparser.get_local_min(subprices, 'Price', 30)
        max = dparser.get_local_max(subprices, 'Price', 30)

        pct_chg = pd.DataFrame({
            'PctChg': (max['Price'] - min['Price']) / min['Price'] * 100
        })

        print(f'--- Min ---\n{min}\n')
        print(f'--- Max ---\n{max}\n')
        print(pct_chg, '\n')


def check_get_delta():
    collector = Collector()
    symbol = 'AI'

    prices = collector.get_prices([symbol], period='60d', interval='2m')[symbol]
    prices = dparser.filter(prices, '2021-01-29', '2021-01-29', '9:30 AM', '4:00 PM')

    rsi = collector.get_rsi([symbol], period='60d', interval='2m')[symbol]
    rsi = dparser.filter(rsi, '2021-01-29', '2021-01-29', '9:30 AM', '4:00 PM')

    print('--- Low RSI ---')
    rsi_lo = dparser.get_local_min(rsi, 'RSI', 30)
    print(rsi_lo, '\n')

    print('--- Low Prices ---')
    price_lo = dparser.get_local_min(prices, 'Price', 30)
    print(price_lo, '\n')

    print('--- High RSI ---')
    rsi_hi = dparser.get_local_max(rsi, 'RSI', 30)
    print(rsi_hi, '\n')

    print('--- High Prices ---')
    prices_hi = dparser.get_local_max(prices, 'Price', 30)
    print(prices_hi, '\n')

    print('--- Lo2Lo R2P Offset ---')
    deltas = dparser.get_delta(rsi_lo, price_lo, 'Time')
    print(deltas)

    print('--- Hi2Hi R2P Offset---')
    deltas = dparser.get_delta(rsi_hi, prices_hi, 'Time')
    print(deltas)

    print('--- Lo2Hi P2P Offset ---')
    deltas = dparser.get_delta(price_lo, prices_hi, 'Time')
    print(deltas)


if __name__ == '__main__':
    # check_filter()
    # check_split()
    # check_local_extrema()
    check_get_delta()
