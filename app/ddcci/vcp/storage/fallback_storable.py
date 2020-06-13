# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta, abstractmethod

from typing import Any, Hashable

from .storage import VcpStorage
from .storable import VcpStorageStorable, T_VcpStorageStorable

from app.util.mixins import HierarchicalMixin, NamedMixin

def wrap_read_method(name):
    def f(self, *args, **kwargs):
        obj = self.get_wrapped_storable()
        _mthd = getattr(obj, name)
        res = _mthd(*args, **kwargs)
        return self._wrap_method_return_value(res)
    f.__name__ = name
    return f

def wrap_property_fget(name):
    def f(self):
        obj = self.get_wrapped_storable()
        res = getattr(obj, name)
        return self._wrap_method_return_value(res)
    f.__name__ = name
    return f

def wrap_write_method(name):
    def f(self, *args, **kwargs):
        obj = self.create_wrapped_storable()
        _mthd = getattr(obj, name)
        return _mthd(*args, **kwargs)
    f.__name__ = name
    return f


class FallbackVcpStorageStorable(HierarchicalMixin, NamedMixin, metaclass=ABCMeta):
    def __init__(self, name : Hashable, parent : VcpStorage):
        super().__init__(instance_name=f"Fallback({name})", instance_parent=parent)

        self._name = name

    @abstractmethod
    def get_wrapped_storable(self, check_fallback) -> T_VcpStorageStorable:
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
                    setattr(cls, mthd_nm, wrap_write_method(mthd_nm))

        for attr_nm in wrapped_cls.__dict__:
            if attr_nm not in cls.__dict__ and attr_nm not in ('__dict__','__weakref__'):
                attr = getattr(wrapped_cls, attr_nm)

                if callable(attr):
                    setattr(cls, attr_nm, wrap_read_method(attr_nm))

                elif isinstance(attr, property):
                    setattr(cls, attr_nm, property(fget=wrap_property_fget(attr_nm)))

    __getattr__ = wrap_read_method('__getattr__')


FallbackVcpStorageStorable.wrap_storable_class(FallbackVcpStorageStorable, VcpStorageStorable)
