#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks forecaster module.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


import config
from forecaster import Forecaster


def check_init_0():
    watchlists = {'Test': ['AAPL', 'MSFT', 'AI', 'DASH']}
    watchlists = config.WATCHLISTS
    for symbols in watchlists.values():
        forecaster = Forecaster(symbols)
        print('=== BASIS ===')
        forecaster.print_basis()
        print('\n=== FEE ===')
        forecaster.print_fee()
        print('\n=== SUMM ===')
        forecaster.print_summ()


def check_export_0():
    # watchlists = {'Test': ['AAPL', 'MSFT', 'AI', 'DASH']}
    watchlists = config.WATCHLISTS
    for watchlist, symbols in watchlists.items():
        forecaster = Forecaster(symbols)
        print('=== BASIS ===')
        forecaster.export_basis(ext='txt')
        print('\n=== FEE ===')
        forecaster.export_fee(ext='txt')
        print('\n=== SUMM ===')
        forecaster.export_summ(
            dir='.', ext='txt', all_in_one=True, watchlist=watchlist)


if __name__ == '__main__':
    check_init_0()
    check_export_0()
