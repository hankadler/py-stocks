#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests rsi module.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


# import datetime as dt
import unittest

# import header
# import logger
from collector import Collector
from indicators.rsi import RSI


class MyTestCase(unittest.TestCase):
    # module  = 'rsi'
    # version = '0.1.0'
    # version = header.get_version(f'../rsi.py')
    # date = dt.datetime.now().strftime('%Y-%m-%d')
    # log = logger.get(__name__, f'{module}-{version}-{date}')
    # result = unittest.TestResult()

    def setUp(self):
        self.symbols = ['MSFT', 'AAPL']
        self.period = '60d'
        self.interval = '2m'
        self.periods = 90

    # def tearDown(self):
    #     print()
    #     if self.result.wasSuccessful():
    #         self.log.info('=== RESULT: PASS ===')
    #     else:
    #         self.log.info('=== RESULT: FAIL ===')

    def test_RSI(self):
        # self.log.info('=== TEST: RSI ===')

        collector = Collector()
        prices = collector.get_prices(
            symbols=self.symbols, period=self.period, interval=self.interval
        )

        rsi = {}
        for k, v in prices.items():
            rsi[k] = RSI(prices[k], 90).data
            print(f'--- {k} ---')
            print(rsi[k].tail(), '\n')

        self.assertEqual(len(rsi), len(self.symbols))


if __name__ == '__main__':
    unittest.main()
