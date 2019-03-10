# -*- coding: utf-8 -*-

"""Main module."""

# from abc import ABC as _ABC
from contextlib import AbstractContextManager as _AbstractContextManager
from abc import abstractmethod as _abstractmethod
# from abc import abstractclassmethod as _abstractclassmethod


class PyPasteBase(_AbstractContextManager):
    @property
    @_abstractmethod
    def clipboard(self):
        return self._clipboard

    @clipboard.setter
    @_abstractmethod
    def clipboard(self, value):
        self._clipboard = value
