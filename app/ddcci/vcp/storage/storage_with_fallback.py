# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Hashable, Any, Union, Set

from .storable import T_VcpStorageStorable
from .storage import VcpStorage
from .fallback_storable import FallbackVcpStorageStorable
from abc import ABCMeta, abstractmethod



class VcpStorageWithFallback(VcpStorage, metaclass=ABCMeta):
    # Fallback property
    @abstractmethod
    def _get_fallback(self) -> Any:
        pass

    @property
    def fallback(self) -> Any:
        return self._get_fallback()

    @abstractmethod
    def _set_fallback(self, new_fallback: Any) -> None:
        pass

    @fallback.setter
    def fallback(self, new_fallback: Any) -> None:
        if self._get_fallback() is not None:
            raise RuntimeError("Not allowed to change the storage fallback more than once")
        if len(self._objs) > 0:
            raise RuntimeError("Not allowed to change the storage fallback with a non-empty storage")
        self._set_fallback(new_fallback)

    @abstractmethod
    def _get_fallback_storage(self) -> VcpStorage:
        pass

    @abstractmethod
    def _wrap_fallback_storable(self, name : Hashable, storable : T_VcpStorageStorable) -> FallbackVcpStorageStorable:
        pass

    # Accesses
    def get(self, name: Hashable, add=True, check_fallback=True, wrap_fallback=True) -> Union[T_VcpStorageStorable, FallbackVcpStorageStorable]:
        # If there's no fallback, just call the super-class
        if self.fallback is None or not check_fallback:
            return super().get(name, add=add)

        # Call the superclass
        try:
            obj = super().get(name, add=False)

        # If we get a KeyError, we don't contain the key. Try the fallback
        except KeyError:
            try:
                obj = self._get_fallback_storage().get(name, add=False)
            except KeyError:
                if not add:
                    raise
            else:
                if wrap_fallback:
                    return self._wrap_fallback_storable(name, obj)
                else:
                    return obj

        # We contain 'name'
        else:
            # An explicit 'None' being stored means we do not check the fallback
            if obj is None and not add:
                raise KeyError(name)

            return obj

        # Doesn't exist here or in the fallback, but add is True, so we simply call the superclass again
        return super().get(name, add=True)


    def remove(self, name: Hashable) -> None:
        key = self.to_key(name)

        # If the fallback contains the key, set it to None
        if self.fallback is not None and self._get_fallback_storage().contains(key):
            self._objs[key] = None
            if key in self._set:
                self._set.remove(key)
            return

        # Otherwise, just call the super-class
        return super().remove(key)


    def contains(self, name: Hashable, check_fallback=True):
        obj = None
        try:
            obj = self.get(name, add=False, check_fallback=check_fallback)
        except KeyError:
            pass
        return obj is not None


    # Iteration
    def _get_set_union(self):
        _set = super()._get_set_union()

        fallback_storage = self._get_fallback_storage()
        if fallback_storage is not None:
            _set = _set.union(fallback_storage._get_set_union())

        for k, v in self._objs.items():
            if v is None:
                _set.remove(k)

        return _set

    def _get_objs_union(self):
        _objs = super()._get_objs_union()

        fallback_storage = self._get_fallback_storage()
        if fallback_storage is not None:
            fallback_objs = dict(fallback_storage._get_objs_union())
            fallback_objs.update(_objs)
            _objs = fallback_objs

        for k, v in self._objs.items():
            if v is None:
                _objs.pop(k)

        return _objs
