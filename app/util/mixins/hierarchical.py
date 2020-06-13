# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from . import shorten_name
from .named import NamedMixin

class HierarchicalMixin(object):
    def __init__(self, *args, instance_parent: 'HierarchicalMixin' = None, **kwargs):
        super().__init__(*args, **kwargs)

        # Sanity check: We must come before Named
        mro = self.__class__.__mro__
        if NamedMixin in mro and mro.index(NamedMixin) < mro.index(HierarchicalMixin):
            raise TypeError(f"'HierarchicalMixin' must come *before* 'NamedMixin' in the MRO")

        self.__parent = instance_parent

    @classmethod
    def class_short_name(cls) -> str:
        return shorten_name(cls.__name__)


    # Parent
    def _set_instance_parent(self, new_parent : 'HierarchicalMixin') -> None:
        if new_parent is not None and not isinstance(new_parent, HierarchicalMixin):
            raise TypeError("'new_parent' must be a class that extends 'HierarchicalMixin'")
        self.__parent = new_parent

    @property
    def instance_parent(self) -> 'HierarchicalMixin':
        return self.__parent
    @instance_parent.setter
    def instance_parent(self, new_parent : 'HierarchicalMixin') -> None:
        self._set_instance_parent(new_parent)


    @property
    def instance_hierarchy(self) -> str:
        hier = self.instance_name if isinstance(self, NamedMixin) else self.__class__.__name__
        if self.__parent is None:
            return hier

        return f"{self.__parent.instance_hierarchy}.{hier}"


    # Printing
    @property
    def __repr_name(self) -> str:
        nm = self.instance_hierarchy
        cnm = self.__class__.__name__

        if cnm in nm:
            return nm
        else:
            return f"{cnm} {nm}"

    def __repr__(self) -> str:
        return f"<{self.__repr_name}>"

    @property
    def __str_name(self) -> str:
        if isinstance(self, NamedMixin):
            return self._NamedMixin__str_name

        return f"{self.__class__.__name__}"

    def __str__(self) -> str:
        return f"<{self.__str_name}>"