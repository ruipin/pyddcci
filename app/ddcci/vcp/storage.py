# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Optional, Hashable, Any, Iterable
from abc import ABCMeta, abstractmethod
from ordered_set import OrderedSet

from app.util import LoggableMixin, HierarchicalMixin



class VcpStorage(LoggableMixin, HierarchicalMixin, metaclass=ABCMeta):
    __slots__ = {"_objs", "_set"}

    def __init__(self, instance_parent=None):
        super().__init__(instance_parent=instance_parent)

        self._objs = {}
        self._set    = set()


    # Utility methods
    @abstractmethod
    def _is_storable_value(self, obj : Any) -> bool:
        pass

    def _transparent_value(self, obj : Any) -> int:
        if self._is_storable_value(obj):
            return obj.vcp_storage_key()
        return obj

    @abstractmethod
    def _create_value(self, value : int) -> 'VcpStorageStorable':
        pass


    # Accesses
    def get(self, key : Hashable, add=True):
        # Transparently accept value objects
        key = self._transparent_value(key)

        # Search for the object
        obj = self._objs.get(key, None)
        if obj is not None:
            return obj

        # Add it if not found
        if add and isinstance(key, int):
            return self.add(key)

        # Otherwise, fail
        raise KeyError(key)


    def add(self, value : int):
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


    def remove(self, key : Hashable) -> None:
        obj = self._objs.get(key, None)
        if obj is None:
            return

        del self._objs[key]

        if isinstance(key, int):
            obj.remove_all_names()
            self._set.remove(obj)
        else:
            obj.remove_name(key)


    def set(self, name : Hashable, value : Optional[int]) -> Optional:
        # Sanity checks
        if isinstance(name, int):
            raise ValueError(f"'name'={name} must not be an integer")

        # Wrap 'remove' if value is None
        if value is None:
            return self.remove(name)

        # Transparently accept value objects
        value = self._transparent_value(value)

        # Check if name already exists
        obj = self._objs.get(name, None)
        if obj is not None:
            if obj.vcp_storage_key() == value:
                return

            obj.remove_name(name)

        # Find a VcpValue if already present, otherwise create one
        obj = self.add(value)

        self._objs[name]  = obj
        obj.add_name(name)

        return obj


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

    def __contains__(self, m):
        return self._objs.__contains__(m)


    # Iteration
    def __iter__(self):
        """ Returns an iterator to the internal dictionary """
        return iter(self._set)

    def __len__(self):
        """ Returns the length of the internal dictionary """
        return len(self._set)

    def keys(self):
        return self._objs.keys()

    def items(self):
        return self._objs.items()

    def values(self):
        return iter(self._set)


    # Printing
    def __repr__(self):
        return f"<{self._LoggableMixin__repr_name}:{repr(self._set)}>"




class VcpStorageStorable(metaclass=ABCMeta):
    def __init__(self, *args, **kwargs):
        instance_parent = None
        if not isinstance(self, HierarchicalMixin):
            instance_parent = kwargs.pop('instance_parent', None)

        super().__init__(*args, **kwargs)

        self._names = OrderedSet()

        if not isinstance(self, HierarchicalMixin):
            self.instance_parent = instance_parent



    @abstractmethod
    def vcp_storage_key(self) -> int:
        pass


    # Name(s)
    @property
    def name(self) -> str:
        if self._names and isinstance(self._names[0], str):
            return self._names[0]
        return f"0x{self.vcp_storage_key():X}"

    @property
    def names(self) -> OrderedSet[str]:
        return OrderedSet(self._names)

    def add_name(self, new_name : Hashable):
        if isinstance(new_name, int):
            raise ValueError(f"new_name={new_name} cannot be an integer")

        self._names.add(new_name)

        if isinstance(self.instance_parent, VcpStorage):
            self.instance_parent[new_name] = self.vcp_storage_key()

    def add_names(self, names : Iterable[Hashable]):
        for name in names:
            self.add_name(name)

    def remove_name(self, name : Hashable):
        if isinstance(name, int):
            raise ValueError(f"name={name} cannot be an integer")

        self._names.remove(name)

        if isinstance(self.instance_parent, VcpStorage):
            del self.instance_parent[name]

    def remove_names(self, names : Iterable[Hashable]):
        for name in names:
            self.remove_name(name)

    def clear_names(self):
        for name in set(self._names):
            self.remove_name(name)


    # Comparison, etc
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other is self

        return other == self.vcp_storage_key()

    def __hash__(self):
        return self.vcp_storage_key()


    # Printing
    def __str__(self):
        return self.name
