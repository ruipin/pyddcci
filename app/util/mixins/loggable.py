# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import re
import logging

from . import shorten_name
from .named import NamedMixin
from .hierarchical import HierarchicalMixin

class LoggableMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Sanity check: We must come before Named
        mro = self.__class__.__mro__
        if NamedMixin in mro and mro.index(NamedMixin) < mro.index(LoggableMixin):
            raise TypeError(f"'LoggableMixin' must come *before* 'NamedMixin' in the MRO")
        if HierarchicalMixin in mro and mro.index(HierarchicalMixin) < mro.index(LoggableMixin):
            raise TypeError(f"'LoggableMixin' must come *before* 'NamedMixin' in the MRO")

        self.__log = None

    @classmethod
    def class_short_name(cls) -> str:
        return shorten_name(cls.__name__)


    # Support for Hierarchical/Named
    def _set_instance_parent(self, new_parent : HierarchicalMixin) -> None:
        super()._set_instance_parent(new_parent)
        self.__log = None

    def _set_instance_name(self, new_name : str) -> None:
        super()._set_instance_name(new_name)
        self.__log = None


    # Logging
    @property
    def log(self) -> logging.Logger:
        """ Returns a logger for the current object. If self.name is 'None', uses the class name """
        if self.__log is None:
            from ..init import getLogger
            parent = self.instance_parent if isinstance(self, HierarchicalMixin) else None
            self._log = getLogger(self.__log_name__, parent=parent)
        return self._log

    @property
    def __log_name__(self) -> str:
        return self.instance_name if isinstance(self, NamedMixin) else self.__class__.__name__

    @property
    def __log_hierarchy__(self) -> str:
        return self.instance_hierarchy if isinstance(self, HierarchicalMixin) else self.__log_name__

    # Printing
    @property
    def __repr_name(self) -> str:
        nm = self.__log_hierarchy__
        cnm = self.__class__.__name__

        if cnm in nm:
            return nm
        else:
            return f"{cnm}:{nm}"

    def __repr__(self) -> str:
        return f"<{self.__repr_name}>"

    @property
    def __str_name(self) -> str:
        if isinstance(self, NamedMixin):
            return self._NamedMixin__str_name

        return f"{self.__class__.__name__}"

    def __str__(self) -> str:
        return f"<{self.__str_name}>"