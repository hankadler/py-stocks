#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Observes stocks and reacts to predefined conditions being met.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


import datetime as dt
import multiprocessing as mp
import textwrap
import time

import plotly.graph_objects as go

from collector import Collector
from forecaster import Forecaster
from alerts import Sender
import config, plotter


class Daemon:
    """An application class that actively observes stocks."""

    OUTDIR = f'{config.DATA}/daemon'
    sender = Sender()

    def __init__(self, symbols, watchlist=None, source=Collector.SOURCES[0],
                 strategy=Forecaster.STRATEGIES[0],
                 destination=Sender.DESTINATIONS[0], **kwargs):
        """
        Parameters:
            symbols (list): Stock symbols.
            watchlist (str): Name of the group of stock symbols.
            source (str): Data source from which to collect stock data.
            strategy (str): Forecasting strategy. See
            `Forecaster.STRATEGIES`.
            destination (str): Alert destination. See
            `Sender.DESTINATIONS`.
        """
        self._is_running = True
        self.watchlist = watchlist
        self.forecaster = Forecaster(symbols, strategy, source)
        self.forecaster.export_summ(dir=self.OUTDIR, ext='txt',
            all_in_one=True, watchlist=watchlist, **kwargs)
        self.sender.destination = destination

    # @Helper
    def _observe(self, plot=False, save=True):
        """Creates and runs the processes that get stock data.

        Parameters:
            plot (bool): Flags generation of `plt` plots (blocking).
            save (bool): Flags SVG export (non-blocking, preffered).
        """
        date = dt.datetime.now().strftime('%I:%M:%S %p')
        mp.log_to_stderr(30)
        print(f'Getting data at {date}...')
        procs = []
        funcs = [self._get_prices, self._get_rsi]
        args = (plot, save)
        for func in funcs:
            proc = mp.Process(target=func, args=args)
            proc.start()
            procs.append(proc)
        for proc in procs:
            proc.join()

    # @Worker
    def _get_prices(self, plot=False, save=True):
        prices = self.forecaster.collector.get_prices(
            self.forecaster.symbols, period=self.forecaster.period,
            interval=self.forecaster.interval)

        if plot:
            plotter.plot_density(prices, 'Price', watchlist=self.watchlist)

        if save:
            plotter.save_density(
                prices, 'Price', watchlist=self.watchlist, dir=self.OUTDIR)

    # @Worker
    def _get_rsi(self, plot=False, save=True):
        rsi = self.forecaster.collector.get_rsi(
            self.forecaster.symbols, period=self.forecaster.period,
            periods=self.forecaster.periods)
        self._on_get_rsi(rsi)

        if plot:
            plotter.plot_density(rsi, 'RSI', watchlist=self.watchlist)

        if save:
            plotter.save_density(
                rsi, 'RSI', watchlist=self.watchlist, dir=self.OUTDIR)

    # @Helper
    def _on_get_rsi(self, rsi: dict):
        """Checks if `rsi` raises flag and sends alert accordingly."""
        # stocks_ = StockFactory.create(self.forecaster.symbols)
        # normvols = []
        # for stock in stocks_:
        #     if stock.history is None:
        #         continue
        #     df = stock.history['Volume']
        #     maxvol = df['Volume'].max()
        #     normvol = ((df['Volume'] / maxvol) * 100).astype(int)
        #     normvols.append(normvol.iloc[-1]['Volume'].item())

        symbols = []
        rsi_min = []
        rsi_low = []
        rsi_now = []
        for symbol in self.forecaster.symbols:
            # Gets RSI status.
            try:
                rsi_min_ = self.forecaster.get_basis(True)[symbol]['RSI'].min()
                rsi_low_ = self.forecaster.summ[symbol]['RSI'].loc['Flag']
                rsi_now_ = rsi[symbol]['RSI'].iloc[-1]
            except:
                continue

            symbols.append(symbol)
            rsi_min.append(rsi_min_)
            rsi_low.append(rsi_low_)
            rsi_now.append(rsi_now_)

            # Sends alert if `rsi_now` falls below `rsi_low` (flag).
            time_now = rsi[symbol]['Time'].iloc[-1]
            if rsi_now <= rsi_low:
                t_0 = time_
                t_1 = self.forecaster.summ[symbol]['Time'].loc['Entry']
                p_1 = self.forecaster.summ[symbol]['PctChg'].loc['Entry']
                t_2 = self.forecaster.summ[symbol]['Time'].loc['Exit']
                p_2 = self.forecaster.summ[symbol]['PctChg'].loc['Exit']
                self._on_rsi_low(symbol, t_0, t_1, p_1, t_2, p_2)

            # Exports status.
            pathout = f'{self.OUTDIR}/{self.watchlist}-Status.svg'
            fig = go.Figure(
                data=[go.Table(
                    header={'values': ['Symbol', 'MinRSI', 'LoRSI', 'NowRSI']},
                    cells={'values': [symbols, rsi_min, rsi_low, rsi_now]}
                )])
            fig.write_image(pathout)

    # @Helper
    def _on_rsi_low(self, symbol: str, t_0: dt.time, t_1: float, p_1: float,
                    t_2: float, p_2: float):
        """Compiles alert and passes it on to `sender`.

        Parameters:
            t_0 (dt.time): Flag time.
            t_1 (float): Forecasted minutes to Entry.
            p_1 (float): Forecasted %chg (drop) to Entry.
            t_2 (float): Forecasted minutes from Entry to Exit.
            p_2 (float): Forecasted %chg (gain) from Entry to Exit.
        """
        # Sets times to '%H:%M %p' format.
        fmt = '%I:%M %p'
        t_flag = t_0.strftime(fmt)
        t_0 = dt.datetime.combine(dt.datetime.today(), t_0)  # -> dt.datetime
        t_entry = t_0 + dt.timedelta(0, t_1 * 60)
        t_exit = t_entry + dt.timedelta(0, t_2 * 60)
        t_entry = t_entry.strftime(fmt)
        t_exit = t_exit.strftime(fmt)

        # Calculates entry and exit prices.
        p_flag = self.forecaster.collector.get_prices(
            symbol, '1d', '2m')[symbol]['Price'].iloc[-1]
        p_entry = p_flag * (1 + (p_1 / 100))
        p_exit = p_entry * (1 + (p_2 / 100))

        message = textwrap.dedent(f"""\n
            \tAlert: {symbol} crossed RSI flag at {t_flag}.
                \tForecasted entry: $ {p_entry:.2f} at {t_entry}.
                \tForecasted exit: $ {p_exit:.2f} at {t_exit}.\n""")

        self.sender.send(message)

    # @Worker
    def _get_volumes(self, plot=False, save=False):
        volumes = self.forecaster.collector.get_volumes(
            self.forecaster.symbols)
        if plot:
            plotter.plot_density(volumes, 'Volume', watchlist=self.watchlist)
        if save:
            plotter.save_density(volumes, 'Volume', watchlist=self.watchlist)

    def start(self, interval=60.0, plot=False, save=True):
        """Starts observation process loop.

        Parameters:
            interval (float): Loop time in seconds.
            plot (bool): Flags generation of `plt` plots (blocking).
            save (bool): Flags SVG export (non-blocking, preffered).
        """
        while self._is_running:
            self._observe(plot, save)
            time.sleep(interval)

    def stop(self):
        """Stops observation process loop."""
        self._is_running = False


if __name__ == '__main__':
    pass
