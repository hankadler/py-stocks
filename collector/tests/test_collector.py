#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests collector module.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


import datetime as dt
import unittest

import header, logger
from collector import Collector


class MyTestCase(unittest.TestCase):
    module  = 'collector'
    version = header.getVersion(f'../collector.py')
    date = dt.datetime.now().strftime('%Y-%m-%d')
    log = logger.get(__name__, f'{module}-{version}-{date}')
    result = unittest.TestResult()

    def setUp(self):
        self.symbols = ['MSFT', 'AAPL']
        self.period = '5d'
        self.interval = '30m'

    def tearDown(self):
        print()
        if self.result.wasSuccessful():
            self.log.info('=== RESULT: PASS ===')
        else:
            self.log.info('=== RESULT: FAIL ===')

    def test_get_prices_returns_properly_sized_dict(self):
        self.log.info('=== TEST: get_prices() returns properly sized dict ===')

        collector = Collector()
        prices = collector.get_prices(
            symbols=self.symbols, period=self.period, interval=self.interval
        )

        for k, v in prices.items():
            print(f'--- {k} ---')
            print(prices[k], '\n')

        self.assertEqual(len(prices), len(self.symbols))

    def test_get_volumes_returns_properly_sized_dict(self):
        self.log.info('=== TEST: get_volumes() returns properly sized dict ===')

        collector = Collector()
        volumes = collector.get_volumes(
            symbols=self.symbols, period=self.period, interval=self.interval
        )

        for k, v in volumes.items():
            print(f'--- {k} ---')
            print(volumes[k], '\n')

        self.assertEqual(len(volumes), len(self.symbols))

    def test_get_rsi_returns_properly_sized_dict(self):
        self.log.info(
            '=== TEST: get_rsi() returns properly sized dict ===')

        collector = Collector()
        rsi = collector.get_rsi(
            symbols=self.symbols, period=self.period,
            interval=self.interval
        )

        for k, v in rsi.items():
            print(f'--- {k} ---')
            print(rsi[k].tail(), '\n')

        self.assertEqual(len(rsi), len(self.symbols))

    def test_prices_df_is_properly_named(self):
        self.log.info(
            '=== TEST: get_prices() returns properly named df ===')

        collector = Collector()
        prices = collector.get_prices(
            symbols='AAPL', period=self.period,
            interval=self.interval
        )

        self.assertEqual(prices['AAPL'].index.name, 'Prices')


if __name__ == '__main__':
    unittest.main()
