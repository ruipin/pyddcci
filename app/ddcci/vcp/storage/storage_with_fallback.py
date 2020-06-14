# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Any, Union, Iterable, Dict, Optional
from . import T_VcpStorageStorable, T_VcpStorageIdentifier, T_VcpStorageKey, T_VcpStorageStandardIdentifier, T_VcpStorageName

from .storage import VcpStorage
from .fallback_storable import FallbackVcpStorageStorable
from abc import ABCMeta, abstractmethod



class VcpStorageWithFallback(VcpStorage, metaclass=ABCMeta):
    def _initialize(self):
        super()._initialize()
        self._fallback = None

    # Fallback property
    @property
    def fallback(self) -> Any:
        return self._fallback

    @fallback.setter
    def fallback(self, new_fallback: Any) -> None:
        if self.fallback is not None:
            raise RuntimeError("Not allowed to change the storage fallback more than once")
        if len(self._dict) > 0:
            raise RuntimeError("Not allowed to change the storage fallback with a non-empty storage")

        self._fallback = new_fallback

    @abstractmethod
    def _get_fallback_storage(self) -> VcpStorage:
        pass

    @abstractmethod
    def _wrap_fallback_storable(self, identifier : T_VcpStorageIdentifier, storable : T_VcpStorageStorable) -> FallbackVcpStorageStorable:
        pass

    # Accesses
    def get(self, identifier : T_VcpStorageIdentifier, add=True, check_fallback=True, wrap_fallback=True) -> Union[T_VcpStorageStorable, FallbackVcpStorageStorable]:
        # If there's no fallback, just call the super-class
        if self.fallback is None or not check_fallback:
            return super().get(identifier, add=add)

        # Call the superclass
        try:
            obj = super().get(identifier, add=False)

        # If we get a KeyError, we don't contain the key. Try the fallback
        except KeyError:
            try:
                obj = self._get_fallback_storage().get(identifier, add=False)
            except KeyError:
                if not add:
                    raise
            else:
                # Double check this isn't a new name for an already existing object
                if isinstance(identifier, T_VcpStorageName):
                    try:
                        _obj = super().get(obj.vcp_storage_key(), add=False)
                    except KeyError:
                        pass
                    else:
                        return _obj

                # Create a fallback wrapper object if requested and return the result
                if wrap_fallback:
                    return self._wrap_fallback_storable(identifier, obj)
                else:
                    return obj

        # We contain 'name'
        else:
            # An explicit 'None' being stored means we do not check the fallback
            if obj is None and not add:
                raise KeyError(identifier)

            return obj

        # Doesn't exist here or in the fallback, but add is True, so we simply call the superclass again
        return super().get(identifier, add=True)


    def remove(self, identifier : T_VcpStorageIdentifier) -> None:
        identifier = self.standardise_identifier(identifier)

        super().remove(identifier)

        # If a fallback exists, mark that this identifier has been explicitly removed by storing 'None'
        if self.fallback is not None:
            self._dict[identifier] = None
            return


    def contains(self, identifier : T_VcpStorageIdentifier, check_fallback=True) -> bool:
        obj = None
        try:
            obj = self.get(identifier, add=False, check_fallback=check_fallback)
        except KeyError:
            pass
        return obj is not None


    # Iteration
    def _get_set_union(self) -> Iterable[T_VcpStorageStorable]:
        _set = super()._get_set_union()

        fallback_storage = self._get_fallback_storage()
        if fallback_storage is not None:
            _set = _set.union(fallback_storage._get_set_union())

            for k, v in self._dict.items():
                if v is None and isinstance(k, T_VcpStorageKey):
                    try:
                        to_remove = fallback_storage.get(k, add=False)
                    except KeyError:
                        pass
                    else:
                        _set.remove(to_remove)

        return _set

    def _get_dict_union(self) -> Dict[T_VcpStorageStandardIdentifier, Optional[T_VcpStorageStorable]]:
        _objs = super()._get_dict_union()

        fallback_storage = self._get_fallback_storage()
        if fallback_storage is not None:
            fallback_objs = dict(fallback_storage._get_dict_union())

            for k, v in self._dict.items():
                if v is None:
                    if k in fallback_objs:
                        popped = fallback_objs.pop(k)

                        if isinstance(k, T_VcpStorageKey):
                            to_pop = set()
                            for obj_k, obj_v in fallback_objs.items():
                                if obj_v is popped:
                                    to_pop.add(obj_k)
                            for to_pop_k in to_pop:
                                fallback_objs.pop(to_pop_k)
                else:
                    fallback_objs[k] = v

            _objs = fallback_objs


        return _objs
