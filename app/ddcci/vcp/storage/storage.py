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
        self._dict : Dict[T_VcpStorageStandardIdentifier, T_VcpStorageStorable] = {}
        self._set  : Set[T_VcpStorageStorable]                                  = set()


    # Utility methods
    @abstractmethod
    def _create_value(self, value : T_VcpStorageKey) -> T_VcpStorageStorable:
        pass

    @classmethod
    def standardise_identifier(cls, identifier : T_VcpStorageIdentifier) -> T_VcpStorageStandardIdentifier:
        if isinstance(identifier, T_VcpStorageKey):
            return identifier

        try:
            if identifier[0:2] == '0x':
                identifier = int(identifier, 16)
            else:
                identifier = int(identifier)
            return identifier
        except ValueError:
            pass

        new_identifier = identifier.lower()
        new_identifier = re.sub('[^a-z0-9]+', '', new_identifier)
        if len(new_identifier) > 0:
            return new_identifier

        return identifier


    # Accesses
    def get(self, identifier : T_VcpStorageIdentifier, add=True) -> T_VcpStorageStorable:
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
            obj.clear_names()
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
    def __iter__(self) -> Iterable[T_VcpStorageStorable]:
        return self.values()

    def __len__(self) -> int:
        return len(self._set)

    def keys(self) -> Iterable[T_VcpStorageKey]:
        for v in self._set:
            yield v.vcp_storage_key()

    def items(self) -> ItemsView[T_VcpStorageKey, T_VcpStorageStorable]:
        return self._dict.items()

    def values(self) -> Iterable[T_VcpStorageStorable]:
        return iter(self._set)

    def names(self) -> Iterable[T_VcpStorageName]:
        for k in self._dict.keys():
            if isinstance(k, str):
                yield k


    # Copying
    def copy_storable(self, other_storable: T_VcpStorageStorable) -> T_VcpStorageStorable:
        identifier = other_storable.vcp_storage_key()

        storable = self.add(identifier)
        storable.copy_storable(other_storable)

        return storable

    def copy_storage(self, other: 'VcpStorage', if_none=False) -> None:
        assert self.__class__ is other.__class__

        # Iterate through all keys in other storage and copy them
        if not if_none or len(self) == 0:
            for storable in other.values():
                self.copy_storable(storable)


    # Conversions
    def asdict(self, recursive=True) -> Dict[T_VcpStorageKey, Any]:
        d = {}

        for k, v in self.items():
            if v is None:
                continue

            if k == v.vcp_storage_key():
                if recursive:
                    v = v.asdict(include_key=False)
                d[k] = v

        return d


    # Serialization
    def serialize(self, diff : 'VcpStorage' = None) -> Union[Dict, str]:
        if diff is None:
            return self.asdict()

        d = self.asdict(recursive=False)
        d_diff = diff.asdict(recursive=False)
        res = {}

        def _add_default(value_i):
            if 'default' not in res:
                res['default'] = str(value_i)
            else:
                res['default'] += f',{value_i}'

        # remove values that match
        for value_i in sorted(d.keys()):
            value_obj = d[value_i]
            if value_i not in d_diff:
                value_d = value_obj.serialize()
                if len(value_d) != 0:
                    res[value_i] = value_d
                else:
                    _add_default(value_i)
                continue

            value_d = value_obj.serialize(diff=d_diff[value_i])

            if len(value_d) > 0:
                res[value_i] = value_d
            else:
                _add_default(value_i)

        if 'default' in res and len(res) == 1:
            res = res['default']

        return res

    def deserialize(self, data : Union[Dict, str], diff : Optional['VcpStorage'] = None) -> None:
        if isinstance(data, str):
            data = {'default': data}

        # Parse defaults
        if 'default' in data:
            defaults = data.pop('default')
            defaults_split = defaults.split(',')

            for value_i in defaults_split:
                value_i = int(value_i)

                if diff is not None and value_i in diff:
                    self.copy_storable(diff[value_i])
                    continue

                self.add(value_i)

        # Parse custom codes
        for value_i, value_d in data.items():
            value = self.add(value_i)

            value_diff = None
            if diff is not None and value_i in diff:
                value_diff = diff[value_i]

            value.deserialize(value_d, diff=value_diff)



    # Printing
    def __repr__(self) -> str:
        return f"<{self._LoggableMixin__repr_name}: {str(list(self._set))}>"