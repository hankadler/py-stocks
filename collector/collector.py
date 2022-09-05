#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collects stock market data from `source`.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


import multiprocessing as mp

import numpy as np
import pandas as pd
import yfinance as yf

from indicators.rsi import RSI


class Collector:
    """A library class that collects stock market data."""

    """list: Sources from which `self` can pull stock market data."""
    SOURCES = ['yfinance', 'iex']

    """dict: Default `intervals` as function of `period`. """
    INTERVALS = {'1d': '5m', '5d': '30m', '1mo': '60m', '60d': '5m',
                 '3mo': '1d', '6mo': '1d', 'ytd': '1d', '1y': '1d', '2y': '1d',
                 '5y': '1d', '10y': '1d', 'max': '1d'}

    """dict: Default `periods` (rolling) as function of `interval`. """
    PERIODS = {'1m': 120, '2m': 120, '5m': 120, '15m': 120, '30m': 120,
               '60m': 120, '1h': 120, '1d': 60}

    def __init__(self, source=SOURCES[0]):
        """
        Parameters:
            source (str): Source from `SOURCES` to collect data from.
        """
        self._source = source

    """source (str): Source from which to collect data."""
    @property
    def source(self):
        return self._source
    @source.setter
    def source(self, value):
        if value not in self.SOURCES:
            raise ValueError(
                f'source = {value} is not valid!'
                f'\nValid values are: {self.SOURCES}'
            )
        self._source = value

    def get_prices(
            self, symbols: any, period='60d', interval=INTERVALS['60d'],
            start: str = None, end: str = None, rounding=2):
        """Gets `symbols` price history from `source`.

        Parameters:
            symbols (any): Stock symbol(s).
            period (str): Look-back period until most recent intraday
            quote to pull data from.
                Valid periods:
                '{n}d' ; n <= 60, '{n}mo' ; n <= ?, '{n}y' ; n <= ?,
                'ytd' and 'max'.
            interval (str): Probing intervals. Valid intervals:
                '{n}m' ; n <= ?, '{n}h' ; n <= ?, '{n}d' ; n <= ?,
                '{n}wk' ; n <= ?, '{n}mo' ; n <= ?,
            start (str): Date indicating period start.
            end (str): Date indicating period end.
            rounding (int): Number of significant digits in decimal.

        Returns:
            dict: Keys are `symbols` (str) and values are price history
            (pd.DataFrame).
        """
        if self.source == 'yfinance':
            get_prices = self._get_prices_yf
        elif self._source == 'iex':
            get_prices = self._get_prices_iex

        if not isinstance(symbols, list):
            symbols = symbols.split()

        # Sets up `args` for parallel processing of `get_prices` via `mp.Pool`.
        args = []
        for symbol in symbols:
            args.append((symbol, period, interval, start, end, rounding))

        # Runs parallel processes.
        with mp.Pool() as pool:
            results = pool.starmap(get_prices, args)

        # Parses `results` into `prices` dictionary.
        prices = {}
        for i in range(len(symbols)):
            prices[symbols[i]] = results[i]

        return prices

    def _get_prices_yf(
            self, symbol: str, period='60d', interval=INTERVALS['60d'],
            start: str = None, end: str = None, rounding=2):
        """Gets `symbol` price history from Yahoo Finance."""
        prices = yf.Ticker(symbol).history(
            period=period, interval=interval, start=start, end=end,
            rounding=rounding
        )['Low'].dropna()

        if prices.empty:
            return pd.DataFrame(
                {'Date': [np.nan],'Time': [np.nan], 'Price': [np.nan]})

        prices = pd.DataFrame({
            'Date': prices.index.date,
            'Time': prices.index.time,
            'Price': prices.values})
        prices.reset_index(drop=True, inplace=True)
        prices.index.rename('Prices', inplace=True)

        return prices

    def _get_prices_iex(self):
        pass

    def get_volumes(
            self, symbols: any, period='60d', interval=INTERVALS['60d'],
            start: str = None, end: str = None, rounding=2, absolute=False):
        """Gets `symbols` volume history (millions) from `source`.

        Parameters:
            symbols (any): Stock symbol(s).
            period (str): Look-back period until most recent intraday
            quote to pull data from.
                Valid periods:
                '{n}d' ; n <= 60, '{n}mo' ; n <= ?, '{n}y' ; n <= ?,
                'ytd' and 'max'.
            interval (str): Probing intervals. Valid intervals:
                '{n}m' ; n <= ?, '{n}h' ; n <= ?, '{n}d' ; n <= ?,
                '{n}wk' ; n <= ?, '{n}mo' ; n <= ?,
            start (str): Date indicating period start.
            end (str): Date indicating period end.
            absolute (bool): Flag for disregarding volume sign.

        Returns:
            dict: Keys are `symbols` (str) and values are volume history
            (pd.DataFrame).
        """
        if self.source == 'yfinance':
            get_volumes = self._get_volumes_yf
        elif self._source == 'iex':
            get_volumes = self._get_volumes_iex

        # Sets up `args` for parallel processing of `get_volumes` via `mp.Pool`.
        args = []
        for symbol in symbols:
            args.append((symbol, period, interval, start, end, absolute))

        # Runs parallel processes.
        with mp.Pool() as pool:
            results = pool.starmap(get_volumes, args)

        # Parses `results` into `volumes` dictionary.
        volumes = {}
        for i in range(len(symbols)):
            volumes[symbols[i]] = results[i]

        return volumes

    def _get_volumes_yf(
            self, symbol: str, period='60d', interval=INTERVALS['60d'],
            start: str = None, end: str = None, rounding=2, absolute=False):
        """Gets `symbol` volume history from Yahoo Finance."""
        volumes = yf.Ticker(symbol).history(
            period=period, interval=interval, start=start, end=end,
        )['Volume'].dropna()

        if volumes.empty:
            return pd.DataFrame({
                'Date': [np.nan],'Time': [np.nan],'Volume': [np.nan]})

        if absolute:
            volumes = volumes.abs()

        volumes = pd.DataFrame({
            'Date': volumes.index.date,
            'Time': volumes.index.time,
            'Volume': volumes.values})
        volumes.reset_index(drop=True, inplace=True)
        volumes.index.rename('Volumes', inplace=True)

        return volumes

    def _get_volumes_iex(self):
        pass

    def get_rsi(
            self, symbols: list, period='60d', interval=INTERVALS['60d'],
            start: str = None, end: str = None, rounding=2,
            periods=PERIODS[INTERVALS['60d']]):
        """Gets RSI history for `symbols`.

        Parameters:
            symbols (any): Stock symbol(s).
            period (str): Look-back period. See `get_prices`.
            interval (str): Probing intervals. See `get_prices`.
            start (str): Date indicating period start.
            end (str): Date indicating period end.
            rounding (int): Number of significant digits in decimal.
            periods (int): Periods for RSI calculation.

        Returns:
            dict: Keys are `symbols` (str) and values are RSI
            (pd.DataFrame).
        """
        prices = self.get_prices(
            symbols, period, interval, start, end, rounding=None
        )

        rsi = {}
        for symbol, data in prices.items():
            if data.isnull().values.any():
                continue
            rsi[symbol] = RSI(prices=data, periods=periods).data[
                ['Date', 'Time', 'RSI']
            ].round(rounding)

        return rsi


if __name__ == '__main__':
    pass
