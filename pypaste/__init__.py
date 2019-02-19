# -*- coding: utf-8 -*-

"""Top-level package for pypaste."""

__author__ = """Joel Travis Frederico"""
__version__ = '0.1.0'

import sys as _sys

if _sys.platform == "darwin":
    from .pypaste_mac import MacPaste as PyPaste

def GetClipboard():
    with PyPaste() as mp:
        return mp.clipboard
