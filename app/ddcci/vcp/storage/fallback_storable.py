# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta, abstractmethod

from typing import Any

from .storage import VcpStorage
from . import VcpStorageStorable, T_VcpStorageStorable, T_VcpStorageIdentifier

from app.util.mixins import HierarchicalMixin, NamedMixin

def wrap_read_method(name):
    def f1(self, *args, **kwargs):
        obj = self.get_wrapped_storable()
        _mthd = getattr(obj, name)
        res = _mthd(*args, **kwargs)
        return self._wrap_method_return_value(res)
    f1.__name__ = name
    return f1

def wrap_write_method(name):
    def f3(self, *args, **kwargs):
        obj = self.create_wrapped_storable()
        _mthd = getattr(obj, name)
        return _mthd(*args, **kwargs)
    f3.__name__ = name
    return f3

def wrap_property(prop : property):
    def fget(self):
        obj = self.get_wrapped_storable()
        return prop.__get__(obj)

    def fset(self, value):
        obj = self.create_wrapped_storable()
        return prop.__set__(obj, value)

    return property(fget=fget, fset=fset)


class FallbackVcpStorageStorable(HierarchicalMixin, NamedMixin, metaclass=ABCMeta):
    def __init__(self, identifier : T_VcpStorageIdentifier, parent : VcpStorage):
        super().__init__(instance_name=f"Fallback({identifier})", instance_parent=parent)

        self._identifier = identifier

    @abstractmethod
    def get_wrapped_storable(self, check_fallback=True) -> T_VcpStorageStorable:
        pass

    @abstractmethod
    def create_wrapped_storable(self):
        pass

    def _wrap_method_return_value(self, value : Any) -> Any:
        return value

    @staticmethod
    def wrap_storable_class(cls, wrapped_cls):
        if 'WRITE_METHODS' in wrapped_cls.__dict__:
            for mthd_nm in wrapped_cls.WRITE_METHODS:

                if mthd_nm not in cls.__dict__:
                    attr = getattr(wrapped_cls, mthd_nm)

                    if callable(attr):
                        setattr(cls, mthd_nm, wrap_write_method(mthd_nm))
                    elif isinstance(attr, property):
                        setattr(cls, mthd_nm, wrap_property(attr))

        for attr_nm in wrapped_cls.__dict__:
            if attr_nm not in cls.__dict__ and attr_nm not in ('__dict__','__weakref__'):
                attr = getattr(wrapped_cls, attr_nm)

                if callable(attr):
                    setattr(cls, attr_nm, wrap_read_method(attr_nm))

                elif isinstance(attr, property):
                    setattr(cls, attr_nm, wrap_property(attr_nm))

    def __getattr__(self, name):
        obj = self.get_wrapped_storable()
        res = getattr(obj, name)
        return self._wrap_method_return_value(res)


FallbackVcpStorageStorable.wrap_storable_class(FallbackVcpStorageStorable, VcpStorageStorable)
