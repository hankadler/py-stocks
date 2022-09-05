#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks rsi module.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


from collector import Collector
from indicators.rsi import RSI


def main():
    collector = Collector()
    prices = collector.get_prices('AAPL')['AAPL']
    rsi_data = RSI(prices, 90).data
    print(rsi_data)


if __name__ == '__main__':
    main()
