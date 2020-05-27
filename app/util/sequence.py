# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta
from collections import MutableSequence

from .hierarchied import Hierarchied


class Sequence(Hierarchied, MutableSequence, metaclass=ABCMeta):
    """
    list wrapper with extended functionality
    """


    # Constructor
    def __init__(self, log_name=None, *args, frozen=False, parent=None, **kwargs):
        """ Initializes a list
        If copy_from is not None, copies the contents from another list """
        super().__init__(log_name=log_name, parent=parent)

        self._frozen   = False

        self._list = list(*args, **kwargs)

        self._frozen = frozen


    # Abstract methods implementation
    def __getitem__(self, i):
        return self._list[i]

    def __setitem__(self, i, v):
        if self._frozen:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")
        self._list[i] = v

    def __delitem__(self, i):
        if self._frozen:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")
        del self._list[i]

    def insert(self, i, v):
        if self._frozen:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")
        self._list.insert(i, v)

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return iter(self._list)


    # List utilities
    def replace(self, other_list):
        if self._frozen:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")

        self._list = list(other_list)


    # Freezing
    def freeze(self, recursive=True):
        if recursive:
            for obj in self:
                if hasattr(obj, 'frozen') and not obj.frozen:
                    obj.freeze()
        self._frozen = True

    def unfreeze(self, recursive=True):
        if recursive:
            for obj in self:
                if hasattr(obj, 'frozen') and obj.frozen:
                    obj.unfreeze()
        self._frozen = False

    @property
    def frozen(self):
        return self._frozen
    @frozen.setter
    def frozen(self, val):
        if val:
            self.freeze()
        else:
            self.unfreeze()


    # Printing
    def __repr__(self):
        return f"<{self._repr_name}:{repr(self._list)}>"

    def repr_list(self):
        return repr(self._list)
