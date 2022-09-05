#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks daemon class.

@author   Hank Adler
@version  0.1.0
@license  MIT
"""


from daemon import Daemon


def check_observe():
    symbols = ['MSFT', 'AAPL']
    Daemon(symbols).start()


if __name__ == '__main__':
    check_observe()
