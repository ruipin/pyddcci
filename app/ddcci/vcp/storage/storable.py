# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro


from typing import Iterable, Dict, Any, Union
from . import T_VcpStorageKey, T_VcpStorageName, T_VcpStorageIdentifier

from abc import ABCMeta, abstractmethod
from ordered_set import OrderedSet

from app.util import HierarchicalMixin

class VcpStorageStorable(metaclass=ABCMeta):
    """ Methods that modify the instance. This list is used to generate wrapper methods automatically in the FallbackVcpStorageStorable classes """
    WRITE_METHODS = ('add_name', 'add_names', 'remove_name', 'remove_names', 'clear_names')


    def __init__(self, *args, **kwargs):
        instance_parent = None
        if not isinstance(self, HierarchicalMixin):
            instance_parent = kwargs.pop('instance_parent', None)

        super().__init__(*args, **kwargs)

        if not isinstance(self, HierarchicalMixin):
            self.instance_parent = instance_parent

        self._initialize()

    def _initialize(self):
        self._names = OrderedSet()

    @abstractmethod
    def vcp_storage_key(self) -> T_VcpStorageKey:
        pass

    @abstractmethod
    def vcp_storage_key_name(self) -> str:
        pass


    # Name(s)
    @property
    def has_name(self) -> bool:
        return len(self._names) > 0

    @property
    def name(self) -> T_VcpStorageName:
        if self.has_name:
            return str(self._names[0])
        return f"0x{self.vcp_storage_key():X}"

    @property
    def names(self) -> Iterable[T_VcpStorageName]:
        return OrderedSet(self._names)

    def add_name(self, new_name : T_VcpStorageName) -> None:
        if isinstance(new_name, int):
            raise ValueError(f"new_name={new_name} cannot be an integer")

        self._names.add(new_name)

        from .storage import VcpStorage
        if isinstance(self.instance_parent, VcpStorage):
            self.instance_parent[new_name] = self.vcp_storage_key()

    def add_names(self, *names : Iterable[T_VcpStorageName]) -> None:
        for name in names:
            self.add_name(name)

    def remove_name(self, name : T_VcpStorageName) -> None:
        if isinstance(name, int):
            raise ValueError(f"name={name} cannot be an integer")

        if name not in self._names:
            return

        self._names.remove(name)

        from .storage import VcpStorage
        if isinstance(self.instance_parent, VcpStorage):
            del self.instance_parent[name]

    def remove_names(self, *names : Iterable[T_VcpStorageName]) -> None:
        for name in names:
            self.remove_name(name)

    def clear_names(self) -> None:
        self.remove_names(*list(self._names))


    # Comparison, etc
    def __eq__(self, other : Union['VcpStorageStorable', T_VcpStorageIdentifier]) -> bool:
        if isinstance(other, self.__class__):
            return other is self

        if isinstance(other, int):
            return other == self.vcp_storage_key()

        if isinstance(other, str):
            from .storage import VcpStorage
            key = VcpStorage.standardise_identifier(other)

            for nm in self.names:
                nm_key = VcpStorage.standardise_identifier(nm)
                if key == nm_key:
                    return True

            return False

        return False

    def __hash__(self) -> int:
        return self.vcp_storage_key()


    # Copying
    def copy_storable(self, other : 'VcpStorageStorable') -> None:
        assert self.vcp_storage_key() == other.vcp_storage_key()
        assert self.__class__ is other.__class__

        self.add_names(*other.names)



    # Conversion
    def asdict(self, include_key=False) -> Dict[str, Any]:
        d = {}

        if self.has_name:
            d['name'] = self.name

            if len(self._names) > 1:
                aliases = []
                for nm in self._names[1:]:
                    aliases.append(str(nm))
                d['aliases'] = aliases

        storage_key_nm = self.vcp_storage_key_name()
        for attr_nm in self.__dict__:
            if attr_nm[0] != '_' and attr_nm != storage_key_nm:
                attr = getattr(self, attr_nm)

                if attr is not None:
                    d[attr_nm] = attr

        if include_key:
            d[storage_key_nm] = self.vcp_storage_key()

        return d


    def _fromdict(self, data : Dict) -> None:
        self.clear_names()

        if 'name' in data:
            self.add_name(data['name'])

        if 'aliases' in data:
            self.add_names(*data['aliases'])

        storage_key_nm = self.vcp_storage_key_name()
        for attr_nm in self.__dict__:
            if attr_nm[0] != '_' and attr_nm != storage_key_nm:
                attr = data.get(attr_nm, None)
                if attr is not None:
                    setattr(self, attr_nm, attr)


    # Printing
    def __str__(self) -> str:
        return self.name
