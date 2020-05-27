# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import re

class Hierarchied(object):
    __slots__ = {"_parent", "_log", "_log_name"}

    def __init__(self, log_name=None, parent=None):
        super().__init__()

        self._parent   = parent
        self._log      = None
        self._log_name = log_name


    # Logging
    @property
    def log(self):
        """ Returns a logger for the current object. If self.name is 'None', uses the class name """
        if self._log is None:
            from . import getLogger
            self._log = getLogger(getattr(self, 'log_name', self), parent=self._parent)
        return self._log

    def _set_log_name(self, new_name):
        if self._log_name == new_name:
            return
        self._log_name = new_name
        self._log = None

    @property
    def log_name(self):
        return self._log_name or self.__class__.__name__
    @log_name.setter
    def log_name(self, new_name):
        self._set_log_name(new_name)

    @property
    def short_class_name(self):
        # Assume camelcase
        res = re.sub('[^A-Z0-9]', '', self.__class__.__name__)

        if res:
            return res

        # Otherwise, do nothing
        return self.__class__.__name__


    # Parent
    def _set_parent(self, new_parent):
        self._parent = new_parent
        self._log = None

    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, new_parent):
        self._set_parent(new_parent)

    @property
    def hierarchy(self):
        hier = self.log_name
        if self._parent is not None:
            hier = f"{self._parent.hierarchy}.{hier}"
        return hier

    @property
    def _repr_name(self):
        if self._parent is not None:
            nm = self.hierarchy
        else:
            nm = self._log_name
            cnm = self.__class__.__name__
            if nm != cnm:
                nm = f"{cnm}:{nm}"
        return nm

    def __repr__(self):
        return f"<{self._repr_name}:{repr(self.__dict__)}>"

    @property
    def _str_name(self):
        nm = self.log_name
        if nm == self.__class__.__name__:
            return self.short_class_name

        if nm.startswith(self.__class__.__name__):
            nm = nm[len(self.__class__.__name__):]

        return f"{self.short_class_name}:{nm}"

    def __str__(self):
        return f"<{self._str_name}>"