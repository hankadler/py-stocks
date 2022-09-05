#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Package configuration.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


import os

import utils


ASSETS_DIR = f'{os.path.dirname(__file__)}/assets'
DATA = f'{os.path.dirname(__file__)}/.data'
symbols = utils.txt2symbols(f'{ASSETS_DIR}/stocks-screened.txt')
WATCHLISTS = utils.symbols2watchlist(symbols, 16)
