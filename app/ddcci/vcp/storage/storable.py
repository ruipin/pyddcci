# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro


from typing import Iterable, Dict, Any, Union
from . import T_VcpStorageKey, T_VcpStorageName

from abc import ABCMeta, abstractmethod
from ordered_set import OrderedSet

from app.util import HierarchicalMixin

class VcpStorageStorable[Storable : VcpStorageStorable](metaclass=ABCMeta):
    """
    Abstract base for objects that can be stored in a VcpStorage.

    Provides naming, serialization, and key management for VCP codes and values.
    Used as a base for VcpCode and VcpValue.
    """

    """ Methods that modify the instance. This list is used to generate wrapper methods automatically in the FallbackVcpStorageStorable classes """
    WRITE_METHODS = ('add_name', 'add_names', 'remove_name', 'remove_names', 'clear_names')


    def __init__(self, *args, **kwargs):
        """
        Initialize the VcpStorageStorable object.

        Args:
            instance_parent: Optional parent instance for hierarchical storage.
        """
        instance_parent = None
        if not isinstance(self, HierarchicalMixin):
            instance_parent = kwargs.pop('instance_parent', None)

        super().__init__(*args, **kwargs)

        if not isinstance(self, HierarchicalMixin):
            self.instance_parent = instance_parent

        self._initialize()

    def _initialize(self):
        """
        Internal initialization method for setting up names.
        """
        self._names = OrderedSet({})

    @abstractmethod
    def vcp_storage_key(self) -> T_VcpStorageKey:
        """
        Return the integer key for storage (code or value).

        Returns:
            int: The storage key.
        """
        pass

    @abstractmethod
    def vcp_storage_key_name(self) -> T_VcpStorageName:
        """
        Return the name of the storage key (e.g., "code" or "value").

        Returns:
            str: The key name.
        """
        pass


    # Name(s)
    @property
    def has_name(self) -> bool:
        """
        Check if this object has a name.

        Returns:
            bool: True if named, False otherwise.
        """
        return len(self._names) > 0

    @property
    def name(self) -> T_VcpStorageName:
        """
        Get the primary name for this object.

        Returns:
            str: The primary name or hex value.
        """
        if self.has_name:
            return str(self._names[0])
        return f"0x{self.vcp_storage_key():X}"

    @property
    def names(self) -> Iterable[T_VcpStorageName]:
        """
        Get all names/aliases for this object.

        Returns:
            Iterable[str]: All names.
        """
        return OrderedSet(self._names)

    def add_name(self, new_name : T_VcpStorageName) -> None:
        """
        Add a new alias name for this object.

        Args:
            new_name: The alias name to add.
        """
        if isinstance(new_name, T_VcpStorageKey):
            raise ValueError(f"new_name={new_name} cannot be a Key type")

        self._names.add(new_name)

        from .storage import VcpStorage
        if isinstance(self.instance_parent, VcpStorage):
            self.instance_parent[new_name] = self.vcp_storage_key()

    def add_names(self, *names : T_VcpStorageName) -> None:
        """
        Add multiple alias names for this object.

        Args:
            names: The alias names to add.
        """
        for name in names:
            self.add_name(name)

    def remove_name(self, name : T_VcpStorageName) -> None:
        """
        Remove an alias name from this object.

        Args:
            name: The alias name to remove.
        """
        if isinstance(name, T_VcpStorageKey):
            raise ValueError(f"name={name} cannot be a Key type")

        if name not in self._names:
            return

        self._names.remove(name)

        from .storage import VcpStorage
        if isinstance(self.instance_parent, VcpStorage):
            del self.instance_parent[name]

    def remove_names(self, *names : T_VcpStorageName) -> None:
        """
        Remove multiple alias names from this object.

        Args:
            names: The alias names to remove.
        """
        for name in names:
            self.remove_name(name)

    def clear_names(self) -> None:
        """
        Remove all alias names from this object.
        """
        self.remove_names(*list(self._names))


    # Comparison, etc
    def __eq__(self, other) -> bool:
        """
        Compare this object with another object or identifier.

        Args:
            other: The object or identifier to compare.

        Returns:
            bool: True if equal, False otherwise.
        """
        if isinstance(other, self.__class__):
            return other is self

        if isinstance(other, T_VcpStorageKey):
            return other == self.vcp_storage_key()

        if isinstance(other, T_VcpStorageName):
            from .storage import VcpStorage
            key = VcpStorage.standardise_identifier(other)

            for nm in self.names:
                nm_key = VcpStorage.standardise_identifier(nm)
                if key == nm_key:
                    return True

            return False

        return False

    def __hash__(self) -> int:
        """
        Generate a hash for this object.

        Returns:
            int: The hash value.
        """
        return self.vcp_storage_key()


    # Copying
    def copy_storable(self, other : Storable) -> None:
        """
        Copy all names from another storable object.

        Args:
            other: The object to copy from.
        """
        assert self.vcp_storage_key() == other.vcp_storage_key()
        assert self.__class__ is other.__class__

        self.add_names(*other.names)



    # Conversion
    def asdict(self, include_key=False) -> Dict[str, Any]:
        """
        Convert this object to a dictionary representation.

        Args:
            include_key: If True, include the storage key in the dict.

        Returns:
            dict: The dictionary representation.
        """
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
        """
        Populate this object from a dictionary.

        Args:
            data: The dictionary to populate from.
        """
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


    # Serialisation
    def serialize(self, diff : Storable|None = None) -> Union[Dict[str, Any], str]:
        """
        Serialise this object to a dictionary.
        Returns:
            dict: The serialised representation.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.serialize() must be implemented by subclasses")

    def deserialize(self, data: Union[Dict, str], diff: Storable|None = None):
        """
        Deserialise this object from a dictionary.
        Args:
            data: The dictionary to deserialise from.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.deserialize() must be implemented by subclasses")


    # Printing
    def __str__(self) -> str:
        """
        Return the primary name as a string.

        Returns:
            str: The primary name.
        """
        return self.name
