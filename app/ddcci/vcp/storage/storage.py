# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import re

from typing import Optional, Iterable, Any, Union, Set, NewType, ItemsView, Dict
from . import VcpStorageStorable, T_VcpStorageStorable, T_VcpStorageName, T_VcpStorageKey, T_VcpStorageIdentifier, T_VcpStorageStandardIdentifier

from abc import ABCMeta, abstractmethod

from app.util import LoggableMixin, HierarchicalMixin, NamedMixin


class VcpStorage(LoggableMixin, HierarchicalMixin, NamedMixin, metaclass=ABCMeta):
    __slots__ = {"_dict", "_set"}

    def __init__(self, instance_parent=None, instance_name=None):
        super().__init__(instance_parent=instance_parent, instance_name=instance_name)
        self._initialize()

    def _initialize(self):
        self._dict : Dict[T_VcpStorageStandardIdentifier, Optional[T_VcpStorageStorable]] = {}
        self._set  : Set[T_VcpStorageStorable]                                            = set()


    # Utility methods
    @abstractmethod
    def _create_value(self, value : T_VcpStorageKey) -> T_VcpStorageStorable:
        pass

    @classmethod
    def standardise_identifier(cls, identifier : T_VcpStorageIdentifier) -> T_VcpStorageStandardIdentifier:
        if isinstance(identifier, T_VcpStorageKey):
            return identifier

        new_identifier = identifier.lower()
        new_identifier = re.sub('[^a-z0-9]+', '', new_identifier)
        if len(new_identifier) > 0:
            return new_identifier

        return identifier


    # Accesses
    def get(self, identifier : T_VcpStorageIdentifier, add=True) -> Optional[T_VcpStorageStorable]:
        identifier = self.standardise_identifier(identifier)

        # Search for the object
        if identifier in self._dict:
            return self._dict[identifier]

        # Add it if not found
        if add and isinstance(identifier, T_VcpStorageKey):
            return self.add(identifier)

        # Otherwise, fail
        raise KeyError(identifier)


    def add(self, key : T_VcpStorageKey) -> T_VcpStorageStorable:
        # If it already exists, just return it
        if key in self._dict:
            return self._dict[key]

        # Otherwise add it
        obj = self._create_value(key)
        self._dict[key] = obj
        self._set.add(obj)
        return obj


    def remove(self, identifier : T_VcpStorageIdentifier) -> None:
        key = self.standardise_identifier(identifier)

        obj = self._dict.get(key, None)
        if obj is None:
            return

        del self._dict[key]

        if isinstance(key, int):
            obj.remove_all_names()
            self._set.remove(obj)
        else:
            obj.remove_name(key)


    def set(self, name : T_VcpStorageName, value : Optional[T_VcpStorageKey]) -> Optional[T_VcpStorageStorable]:
        # Sanity checks
        if not isinstance(name, str):
            raise ValueError(f"'name'={name} must be of type 'str'")

        # Sanity checks
        if value is not None and not isinstance(value, int):
            raise ValueError(f"'value'={value} must be of type 'int'")

        # Convert to key
        identifier = self.standardise_identifier(name)

        # Wrap 'remove' if value is None
        if value is None:
            return self.remove(identifier)

        # Check if name already exists
        obj = self._dict.get(identifier, None)
        if obj is not None:
            if obj.vcp_storage_key() == value:
                return
            obj.remove_name(name)

        # Find a VcpValue if already present, otherwise create one
        obj = self.add(value)

        self._dict[identifier] = obj
        obj.add_name(name)

        return obj


    def contains(self, obj : Union[T_VcpStorageIdentifier, T_VcpStorageStorable]):
        if isinstance(obj, VcpStorageStorable):
            return obj in set
        return self.standardise_identifier(obj) in self._dict



    # Magic methods
    def __getitem__(self, identifier : T_VcpStorageIdentifier) -> T_VcpStorageStorable:
        """ Get an attribute using dictionary syntax obj[key] """
        return self.get(identifier)

    def __setitem__(self, name : T_VcpStorageName, value : T_VcpStorageKey) -> None:
        """ Modify an attribute using dictionary syntax obj[key] = value """
        self.set(name, value)

    def __delitem__(self, identifier : T_VcpStorageIdentifier):
        """ Delete an attribute using dictionary syntax """
        self.remove(identifier)

    def __contains__(self, identifier : Union[T_VcpStorageIdentifier, T_VcpStorageStorable]):
        return self.contains(identifier)


    # Iteration
    def _get_set_union(self) -> Set[T_VcpStorageStorable]:
        return self._set

    def _get_dict_union(self) -> Dict[T_VcpStorageStandardIdentifier, Optional[T_VcpStorageStorable]]:
        return self._dict

    def __iter__(self, fallback=True) -> Iterable[T_VcpStorageStorable]:
        s = self._get_set_union() if fallback else self._set
        return iter(s)

    def __len__(self, fallback=True) -> int:
        s = self._get_set_union() if fallback else self._set
        return len(s)

    def keys(self, fallback=True) -> Iterable[T_VcpStorageKey]:
        for v in self.__iter__(fallback=fallback):
            yield v.vcp_storage_key()

    def items(self, fallback=True) -> ItemsView[T_VcpStorageKey, T_VcpStorageStorable]:
        d = self._get_dict_union() if fallback else self._dict
        return d.items()

    def values(self, fallback=True) -> Iterable[T_VcpStorageStorable]:
        s = self._get_set_union() if fallback else self._set
        return iter(s)

    def names(self, fallback=True) -> Iterable[T_VcpStorageName]:
        d = self._get_dict_union() if fallback else self._dict
        for k in d.keys():
            if isinstance(k, str):
                yield k


    # Conversions
    def asdict(self) -> Dict[T_VcpStorageKey, Optional[Dict]]:
        d = {}

        for k, v in self.items(fallback=False):
            if v is None:
                d[k] = None
            elif k == v.vcp_storage_key():
                _v = v.asdict()
                del _v[v.vcp_storage_key_name()]
                d[k] = _v

        return d


    # Printing
    def __repr__(self) -> str:
        return f"<{self._LoggableMixin__repr_name}: {str(list(self._set))}>"