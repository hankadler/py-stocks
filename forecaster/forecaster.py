#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Makes forecasts.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


import datetime as dt
import os
import time

import numpy as np
import pandas as pd
from scipy.signal import argrelmin, argrelmax

import args2fields as a2f
import config, dparser, xport
from collector import Collector


class Forecaster:
    """A library class for making forecasts."""

    STRATEGIES = ['r2p_extrema']
    OUTDIR = f'{config.DATA}/forecasts'

    def __init__(self, symbols=[], strategy=STRATEGIES[0],
                 source=Collector.SOURCES[0], **kwargs):
        self._kwargs = kwargs
        self._symbols = []
        self._strategy = self.STRATEGIES[0]
        self.collector = Collector(source)
        self.basis = None
        self.summ = None
        self.strategy = strategy
        if symbols:
            self.symbols = symbols

    """symbols (list): Stock symbols."""
    @property
    def symbols(self):
        return self._symbols
    @symbols.setter
    def symbols(self, value):
        if isinstance(value, str):
            value = value.split()
        if not isinstance(value, list):
            raise ValueError(f'symbols = {value} not a str or list!')
        self._symbols = value
        self._on_set_symbols(**self._kwargs)

    """strategy (str): Forecaster strategy."""
    @property
    def strategy(self):
        return self._strategy
    @strategy.setter
    def strategy(self, value):
        if value not in self.STRATEGIES:
            raise ValueError(
                f'strategy = {value} is not valid!'
                f'\nValid values are: {self.STRATEGIES}'
            )
        self._strategy = value

    # @Callback
    def _on_set_symbols(self, **kwargs):
        """Initializes instance fields per `strategy`."""
        print(f"Initializing forecasts for:\n"
              f"    symbols  = {self.symbols}\n"
              f"    strategy = '{self.strategy}'\n")

        if self.strategy == self.STRATEGIES[0]:
            fields = {'period': str, 'interval': str, 'order': int,
                      'periods': int, 'thresh': float}
            defaults = {'period': '30d', 'interval': '5m',
                        'periods': Collector.PERIODS['5m'], 'order': 30,
                        'thresh': 12.5}
            a2f.args2fields(self, fields, defaults=defaults, **kwargs)

            self._set_prices(period=self.period, interval=self.interval)
            self._set_rsi(period=self.period, interval=self.interval)

            # --- DEBUG ---
            # for df in self.prices.values():
            #     print(df)
            # for df in self.rsi.values():
            #     print(df)

            self._set_basis_0()
            self._set_fee_0()
            self._set_summ_0()

    # @Helper
    def _set_prices(self, period, interval):
        prices = self.collector.get_prices(self.symbols, period, interval)

        for sym, df in prices.items():
            if df['Price'].isnull().sum():
                print(f'No data for {sym}! Eliminating from `symbols`...')
                self._symbols.remove(sym)

        self.prices = self.collector.get_prices(self.symbols, period, interval)

    # @Helper
    def _set_rsi(self, period, interval):
        self.rsi = self.collector.get_rsi(self.symbols, period, interval)

    # @Helper
    def _set_basis_0(self):
        """Sets `basis` per strategy 0.

        `basis`: dict
            keys: str -> `symbols`
            vals: list
                items: pd.DataFrame
                    index: int
                    cols -> Date|Time|Price|RSI|LoRSI|LoPrice|HiRSI|
                            HiPrice
        """
        self.basis = {}

        for s, df in self.prices.items():
            if df.isnull().values.any():
                continue
            self.basis[s] = df.copy()
            self.basis[s]['RSI'] = self.rsi[s]['RSI']
            self.basis[s] = self.basis[s][self.basis[s]['RSI'].notna()]

        for s, df in self.basis.items():
            self.basis[s] = dparser.split(df, interval='1d')

        # --- DEBUG ---
        # for ls in self.basis.values():
        #     for df in ls:
        #         print(df)

        # Adds LoRSI, LoPrice, HiRSI, HiPrice columns to `basis`.
        for s, ls in self.basis.items():
            for df in ls:
                df['LoRSI'] = df.iloc[
                    argrelmin(df['RSI'].values, order=self.order)[0]
                ]['RSI']
                df['LoPrice'] = df.iloc[
                    argrelmin(df['Price'].values, order=self.order)[0]
                ]['Price']
                df['HiRSI'] = df.iloc[
                    argrelmax(df['RSI'].values, order=self.order)[0]
                ]['RSI']
                df['HiPrice'] = df.iloc[
                    argrelmax(df['Price'].values, order=self.order)[0]
                ]['Price']
                df.index.name = 'Basis'

        # Reduces `basis`.
        # for s, ls in self.basis.items():
        #     for df in ls:
        #         df.dropna(axis=0, how='all', thresh=5, inplace=True)

        #--- DEBUG ---
        # for ls in self.basis.values():
        #     for df in ls:
        #         print(df, '\n')

    # @Helper
    def _set_fee_0(self):
        """Sets `fee`, the 'Flag-Entry-Exit' dataset per strategy 0.

        `fee`: dict
            keys: str -> `symbols`
            vals: list
                items: pd.DataFrame
                    index.name: str -> Date
                    index: str -> ['Flag', 'Entry', 'Exit']
                    cols: -> Time|RSI|PctChg
        """
        self.fee = {}

        lo_rsi = {}  # Level beyond which data will be ignored.
        for s, df in self.get_basis(flatten=True).items():
            min_rsi = df['RSI'].min()
            max_rsi = df['RSI'].max()
            lo_rsi_a = min_rsi + (self.thresh / 100) * (max_rsi - min_rsi)
            lo_rsi_b = np.percentile(df['RSI'].values, self.thresh)
            lo_rsi[s] = min(lo_rsi_a, lo_rsi_b)

        for s, ls in self.basis.items():
            self.fee[s] = []

            for df in ls:
                try:
                    t_flag = df[df.LoRSI == df.LoRSI.min()]['Time'].item()
                    t_entry = df[df.LoPrice == df.LoPrice.min()]['Time'].item()
                    t_exit = df[df.HiRSI == df.HiRSI.max()]['Time'].item()
                except ValueError:
                    continue

                t_flag = dt.datetime.combine(dt.datetime.today(), t_flag)
                t_entry = dt.datetime.combine(dt.datetime.today(), t_entry)
                t_exit = dt.datetime.combine(dt.datetime.today(), t_exit)

                delta_entry = (t_entry - t_flag).total_seconds() / 60
                delta_exit = (t_exit - t_entry).total_seconds() / 60

                if (delta_entry < 0) or (delta_exit < 0):
                    continue

                rsi_flag = df['LoRSI'].min()

                if rsi_flag > lo_rsi[s]:
                    continue

                price_flag = df[df.LoRSI == rsi_flag]['Price'].item()

                price_entry = df['LoPrice'].min()
                rsi_entry = df[df.LoPrice == price_entry]['RSI'].iloc[0]

                rsi_exit = df['HiRSI'].max()
                price_exit = df[df.HiRSI == rsi_exit]['Price'].iloc[0]

                chg_entry = round(
                    (price_entry - price_flag) / price_flag * 100, 2)
                chg_exit = round(
                    (price_exit - price_entry) / price_entry * 100, 2)

                flag_df = pd.DataFrame({
                    'Time': t_flag.strftime('%I:%M %p'),
                    'RSI': rsi_flag,
                    'PctChg': price_flag
                }, index=['Flag'])
                entry_df = pd.DataFrame({
                    'Time': delta_entry,
                    'RSI': rsi_entry,
                    'PctChg': chg_entry
                }, index=['Entry'])
                exit_df = pd.DataFrame({
                    'Time': delta_exit,
                    'RSI': rsi_exit,
                    'PctChg': chg_exit
                }, index=['Exit'])

                date = df['Date'].iloc[-1]
                merged_df = pd.concat(
                    [flag_df, entry_df, exit_df],
                )
                merged_df.index.name = date
                self.fee[s].append(merged_df)

    # @Helper
    def _set_summ_0(self):
        """Sets forecast summary for strategy 0.

         `summ`: dict
            keys: str -> `symbols`
            vals: pd.DataFrame
                index.name: str -> MinRSI
                index: str -> ['Flag', 'Entry', 'Exit']
                cols: -> Time|RSI|PctChg
        """
        self.summ = {}

        if not (self.basis and self.fee):
            return

        # Gets FEE values from `fee`.
        for s, ls in self.fee.items():
            t_0 = []
            rsi_0 = []
            t_1 = []
            rsi_1 = []
            pctchg_1 = []
            t_2 = []
            rsi_2 = []
            pctchg_2 = []

            for df in ls:
                t_0.append(dt.datetime.strptime(
                    df['Time']['Flag'], '%I:%M %p').time())
                rsi_0.append(df['RSI']['Flag'])
                t_1.append(df['Time']['Entry'])
                rsi_1.append(df['RSI']['Entry'])
                pctchg_1.append(df['PctChg']['Entry'])
                t_2.append(df['Time']['Exit'])
                rsi_2.append(df['RSI']['Exit'])
                pctchg_2.append(df['PctChg']['Exit'])

            # Reduces Fee values.
            try:
                t_0_avg = sum([
                    int(dt.timedelta(hours=t.hour, minutes=t.minute,
                                     seconds=t.second).total_seconds()
                        ) for t in t_0]) / len(t_0)
                t_0 = time.strftime('%I:%M %p', time.gmtime(t_0_avg))
            except:
                t_0 = np.nan
            min_rsi = self.get_basis(flatten=True)[s]['RSI'].min()
            rsi_0 = round(pd.Series(rsi_0).mean(), 2)
            t_1 = round(pd.Series(t_1).mean(), 2)
            rsi_1 = round(pd.Series(rsi_1).quantile(q=0.25), 2)
            pctchg_1 = round(pd.Series(pctchg_1).mean(), 2)
            t_2 = round(pd.Series(t_2).quantile(q=0.25), 2)
            rsi_2 = round(pd.Series(rsi_2).mean(), 2)
            pctchg_2 = round(pd.Series(pctchg_2).quantile(q=0.25), 2)

            # Generate df that will hold reduced values.
            flag_df = pd.DataFrame({
                'Time': t_0,
                'RSI': rsi_0,
                'PctChg': 0.0
            }, index=['Flag'])
            entry_df = pd.DataFrame({
                'Time': t_1,
                'RSI': rsi_1,
                'PctChg': pctchg_1
            }, index=['Entry'])
            exit_df = pd.DataFrame({
                'Time': t_2,
                'RSI': rsi_2,
                'PctChg': pctchg_2
            }, index=['Exit'])

            merged_df = pd.concat([flag_df, entry_df, exit_df])
            merged_df.index.name = f'MinRSI: {min_rsi}'
            self.summ[s] = merged_df

    # @Accessor
    def get_basis(self, flatten=False):
        """Returns the data basis for all forecasts."""
        if flatten:
            basis_flat = {}

            for s, ls in self.basis.items():
                basis_flat[s] = pd.concat(ls)

            # --- DEBUG ---
            # for df in self.basis_flat.values():
            #     print(df, '\n')

            return basis_flat

        return self.basis

    def print_basis(self):
        for s, df in self.get_basis(flatten=True).items():
            print(f'--- {s} ---')
            print(df, '\n')

    def print_fee(self):
        for s, ls in self.fee.items():
            print(f'--- {s} ---')
            for df in ls:
                print(df, '\n')

    def print_summ(self):
        for s, df in self.summ.items():
            print(f'--- {s} ---')
            print(df, '\n')

    def export_basis(self, dir='', ext='txt'):
        if not dir:
            dir = \
                f'{self.OUTDIR}/basis/{dt.datetime.now().strftime("%Y-%m-%d")}'
        xport.export(self.get_basis(flatten=True), dir, ext)

    def export_fee(self, dir='', ext='txt'):
        fee = {}
        for s, ls in self.fee.items():
            try:
                fee[s] = pd.concat(ls)
            except:
                continue
        if not dir:
            dir = f'{self.OUTDIR}/fee/{dt.datetime.now().strftime("%Y-%m-%d")}'
        xport.export(fee, dir, ext)

    def export_summ(self, dir='', ext='txt', all_in_one=False, watchlist=''):
        summ = {}
        for s, df in self.summ.items():
            summ[s] = df
        if not dir:
            dir = \
                f'{self.OUTDIR}/summ/{dt.datetime.now().strftime("%Y-%m-%d")}'
        if all_in_one:
            pathout = f'{dir}/{watchlist}__all__.{ext}'
            if not os.path.isdir(dir):
                os.mkdir(dir)
            if os.path.exists(pathout):
                os.remove(pathout)
            for s, df in self.summ.items():
                with open(pathout, 'a') as fh:
                    fh.write(f'--- {s} ---\n')
                    df.to_string(fh)
                    fh.write('\n\n')
            print(f"Data exported to '{pathout}'.")
        else:
            xport.export(summ, dir, ext)


if __name__ == '__main__':
    pass
