#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Relative Strength Index.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


import pandas as pd


class RSI:
    """A library class to calculate RSI from stock prices."""

    # --- Constructor ---
    def __init__(self, prices, periods):
        """
        Parameters:
            prices (pd.DataFrame): Stock prices.
            periods (int): Window size for `prices` rolling operations.
        """
        # --- Instance Fields ---
        self.data = self.calculate(prices, periods)
        self.periods = periods

    @staticmethod
    def calculate(prices, periods):
        """Calculates RSI(`periods`) on `prices`.

        Parameters:
            prices (pd.DataFrame): Stock prices.
            periods (int): Window size for `prices` rolling operations.

        Returns:
            pd.DataFrame:
                Index: Default
                Columns: Date, Time, Price, Gain, Loss, AvgGain,
                         AvgLoss, RSI
        """
        changes = prices['Price'].pct_change()

        gains = changes.copy()
        gains[changes <= 0] = 0.0

        losses = abs(changes.copy())
        losses[changes > 0] = 0.0

        avg_gain = gains.rolling(periods).mean()
        avg_loss = losses.rolling(periods).mean()

        rsi = 100 - 100 / (1 + avg_gain / avg_loss)

        data = pd.DataFrame({
            'Date': prices['Date'],
            'Time': prices['Time'],
            'Price': prices[prices.columns[-1]],
            'Change': changes,
            'Gain': gains,
            'Loss': losses,
            'AvgGain': avg_gain,
            'AvgLoss': avg_loss,
            'RSI': rsi
        })
        data.reset_index(drop=True, inplace=True)
        data.index.rename('RSI', inplace=True)

        return data

    # --- Instance Methods ---
    def append(self, prices=None):
        """
        Appends prices to `data` and updates other columns.

        Parameters:
            prices (pd.DataFrame)
        """
        if prices is None:
            return

        self.data = pd.concat(
            [self.data, self.calculate(prices, self.periods)]
        )


if __name__ == '__main__':
    pass
