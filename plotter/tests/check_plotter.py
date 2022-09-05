#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks plotter module.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


from collector import Collector
import plotter


COLLECTOR = Collector()
SYMBOLS = {
    1: ['MSFT'],
    2: ['AAPL', 'AMZN'],
    3: ['INTC', 'XOM', 'T'],
    4: ['KO', 'UAL', 'JBLU', 'AAL'],
    9: ['ABNB', 'AFRM', 'AI', 'DASH', 'PLTR', 'SPOT', 'TER', 'U', 'UBER']
}


def check_plot_density():
    symbols = SYMBOLS[9]
    prices = COLLECTOR.get_prices(symbols, '60d', '1d')
    rsi = COLLECTOR.get_rsi(symbols, '60d', '2m')
    plotter.plot_density(prices, 'Price')
    plotter.plot_density(rsi, 'RSI')


def check_save_density():
    symbols = SYMBOLS[9]
    prices = COLLECTOR.get_prices(symbols, '60d', '2m')
    rsi = COLLECTOR.get_rsi(symbols, '60d', '2m')
    plotter.save_density(prices, 'Price', show=False)
    plotter.save_density(rsi, 'RSI', show=False)


def check_plot_scatter():
    symbols = SYMBOLS[1]
    prices = COLLECTOR.get_prices(symbols, '1d', '5m')
    plotter.plot_scatter(prices, 'Time', 'Price')


def check_plot_bar():
    symbols = SYMBOLS[9]
    volumes = COLLECTOR.get_volumes(symbols, '15d', '1d')
    plotter.plot_bar(volumes, 'Date', 'Volume')


if __name__ == '__main__':
    check_plot_density()
    check_save_density()
    check_plot_scatter()
    check_plot_bar()
