# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro


from typing import Hashable, Iterable, TypeVar
from abc import ABCMeta, abstractmethod
from ordered_set import OrderedSet

from app.util import HierarchicalMixin


class VcpStorageStorable(metaclass=ABCMeta):
    """ Methods that modify the instance. This list is used to generate wrapper methods automatically in the FallbackVcpStorageStorable classes """
    WRITE_METHODS = ('add', 'remove', 'set', 'add_name', 'add_names', 'remove_name', 'remove_names', 'clear_names')


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

        from .storage import VcpStorage
        if isinstance(self.instance_parent, VcpStorage):
            self.instance_parent[new_name] = self.vcp_storage_key()

    def add_names(self, names : Iterable[Hashable]):
        for name in names:
            self.add_name(name)

    def remove_name(self, name : Hashable):
        if isinstance(name, int):
            raise ValueError(f"name={name} cannot be an integer")

        self._names.remove(name)

        from .storage import VcpStorage
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

        if isinstance(other, int):
            return other == self.vcp_storage_key()

        if isinstance(other, str):
            return other in self.names

        return False

    def __hash__(self):
        return self.vcp_storage_key()


    # Printing
    def __str__(self):
        return self.name

T_VcpStorageStorable = TypeVar('T_VcpStorageStorable', bound=VcpStorageStorable, covariant=True)