# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta
from collections import MutableSequence


class Sequence(MutableSequence, metaclass=ABCMeta):
    """
    list wrapper with extended functionality
    """

    # If True, allows changing the parent when frozen
    FROZEN_ALLOW_SET_PARENT = False
    # If True, allows changing the log name when frozen
    FROZEN_ALLOW_SET_LOG_NAME = False


    # Constructor
    def __init__(self, log_name=None, *args, frozen=False, parent=None, **kwargs):
        """ Initializes a list
        If copy_from is not None, copies the contents from another list """
        self._log_name = self.__class__.__name__ if log_name is None else log_name
        self._log      = None
        self._frozen   = False
        self._parent   = parent

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


    # Logging
    @property
    def log(self):
        """ Returns a logger for the current object. If self.name is 'None', uses the class name """
        if self._log is None:
            from .log_init import getLogger
            self._log = getLogger(getattr(self, 'log_name', self), parent=self._parent)
        return self._log

    @property
    def log_name(self):
        return self._log_name
    @log_name.setter
    def log_name(self, new_name):
        if self._log_name == new_name:
            return
        if not self.__class__.FROZEN_ALLOW_SET_LOG_NAME and self._frozen:
            raise RuntimeError("Object is frozen!")
        self._log_name = new_name
        self._log = None


    # Parent
    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, new_parent):
        if not self.__class__.FROZEN_ALLOW_SET_PARENT and self._frozen:
            raise RuntimeError("Object is frozen!")
        self._parent = new_parent
        self._log = None

    @property
    def hierarchy(self):
        hier = self._log_name
        if self._parent is not None:
            hier = f"{self._parent.hierarchy}.{hier}"
        return hier


    # Printing
    def __repr__(self):
        if self._parent is not None:
            nm = self.hierarchy
        else:
            nm = self._log_name
            cnm = self.__class__.__name__
            if nm != cnm:
                nm = f"{cnm}:{nm}"

        return f"<{nm} {repr(self._list)}>"

    def __str__(self):
        return f"<{self._log_name}>"

    def repr_list(self):
        return repr(self._list)
