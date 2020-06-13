# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import re

from typing import Optional, Hashable, Any, Dict, Union, Set
from .storable import T_VcpStorageStorable
from abc import ABCMeta, abstractmethod

from app.util import LoggableMixin, HierarchicalMixin, NamedMixin



class VcpStorage(LoggableMixin, HierarchicalMixin, NamedMixin, metaclass=ABCMeta):
    __slots__ = {"_objs", "_set"}

    def __init__(self, instance_parent=None, instance_name=None):
        super().__init__(instance_parent=instance_parent, instance_name=instance_name)

        self._objs : Dict[Hashable, Optional[T_VcpStorageStorable]] = {}
        self._set  : Set[Hashable]                                  = set()


    # Utility methods
    @abstractmethod
    def _is_storable_value(self, obj : Any) -> bool:
        pass

    def _transparent_value(self, obj : Any) -> int:
        if self._is_storable_value(obj):
            return obj.vcp_storage_key()
        return obj

    @abstractmethod
    def _create_value(self, value : int) -> T_VcpStorageStorable:
        pass

    @staticmethod
    def to_key(name : Hashable):
        if not isinstance(name, str):
            return name

        new_key = name.lower()
        new_key = re.sub('[^a-z0-9]+', '', new_key)
        if len(new_key) > 0:
            return new_key

        return name

    # Accesses
    def get(self, name : Hashable, add=True) -> Union[T_VcpStorageStorable, None]:
        key = self.to_key(name)

        # Search for the object
        if key in self._objs:
            return self._objs[key]

        # Add it if not found
        if add and isinstance(key, int):
            return self.add(key)

        # Otherwise, fail
        raise KeyError(key)


    def add(self, value : Union[int, T_VcpStorageStorable]):
        # Transparently accept value objects
        value = self._transparent_value(value)

        # If it already exists, just return it
        if value in self._objs:
            return self._objs[value]

        # Otherwise add it
        obj = self._create_value(value)
        self._objs[value] = obj
        self._set.add(obj)
        return obj


    def remove(self, name : Hashable) -> None:
        key = self.to_key(name)

        obj = self._objs.get(key, None)
        if obj is None:
            return

        del self._objs[key]

        if isinstance(key, int):
            obj.remove_all_names()
            self._set.remove(obj)
        else:
            obj.remove_name(key)


    def set(self, name : Hashable, value : Optional[int]) -> Optional[T_VcpStorageStorable]:
        # Sanity checks
        if isinstance(name, int):
            raise ValueError(f"'name'={name} must not be an integer")

        # Convert to key
        key = self.to_key(name)

        # Wrap 'remove' if value is None
        if value is None:
            return self.remove(key)

        # Transparently accept value objects
        value = self._transparent_value(value)

        # Check if name already exists
        obj = self._objs.get(key, None)
        if obj is not None:
            if obj.vcp_storage_key() == value:
                return
            obj.remove_name(name)

        # Find a VcpValue if already present, otherwise create one
        obj = self.add(value)

        self._objs[key] = obj
        obj.add_name(name)

        return obj


    def contains(self, name : Hashable):
        return self.to_key(name) in self._objs



    # Magic methods
    def __getitem__(self, key : Hashable):
        """ Get an attribute using dictionary syntax obj[key] """
        return self.get(key)

    def __setitem__(self, key : Hashable, value : int):
        """ Modify an attribute using dictionary syntax obj[key] = value """
        self.set(key, value)

    def __delitem__(self, key : Hashable):
        """ Delete an attribute using dictionary syntax """
        self.remove(key)

    def __contains__(self, key : Hashable):
        return self.contains(key)


    # Iteration
    def _get_set_union(self) -> Set[Hashable]:
        return self._set

    def _get_objs_union(self) -> Dict[Hashable, Optional[T_VcpStorageStorable]]:
        return self._objs

    def __iter__(self):
        """ Returns an iterator to the internal dictionary """
        return iter(self._get_set_union())

    def __len__(self):
        """ Returns the length of the internal dictionary """
        return len(self._get_set_union())

    def keys(self):
        return self._get_objs_union().keys()

    def items(self):
        return self._get_objs_union().items()

    def values(self):
        return self.__iter__()

    def names(self):
        for k in self.keys():
            if isinstance(k, str):
                yield k


    # Printing
    def __repr__(self):
        return f"<{self._LoggableMixin__repr_name}: {str(list(self._set))}>"