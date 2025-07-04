# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta
from collections.abc import MutableSequence
from dataclasses import is_dataclass, asdict as dataclass_asdict
from typing import Any, Dict, Iterator, List

from .namespace import Namespace
from ..mixins import *
from ..enter_exit_call import EnterExitCall


class NamespaceList[T](Namespace, MutableSequence, metaclass=ABCMeta):
    """
    A list wrapper with extended functionality, supporting both list and namespace behaviors.

    Provides a mutable sequence with attribute access, freezing, and mixin support. Used for ordered collections
    of configuration or data objects in pyddcci.
    """

    # Constructor
    def __init__(self, *args, frozen_schema=False, frozen_namespace=False, frozen_list=False, **kwargs):
        """
        Initializes a NamespaceList instance.
        Args:
            frozen_schema (bool): If True, freeze the schema.
            frozen_namespace (bool): If True, freeze the namespace.
            frozen_list (bool): If True, freeze the list.
            *args: Positional arguments for list initialization.
            **kwargs: Keyword arguments for list initialization.
        """
        # Call super-class
        super_params = {'frozen_schema': frozen_schema, 'frozen_namespace': frozen_namespace}
        if isinstance(self, NamedMixin):
            super_params['instance_name'] = kwargs.pop('instance_name', None)
        if isinstance(self, HierarchicalMixin):
            super_params['instance_parent'] = kwargs.pop('instance_parent', None)
        super().__init__(**super_params)

        self.__frozen_list   = False

        self._list : List[T] = list(*args, **kwargs)

        self.__frozen_list = frozen_list


    # Abstract methods implementation
    def __getitem__(self, i : int) -> T:
        """
        Get an item from the list by index.
        Args:
            i (int): Index of the item.
        Returns:
            object: The item at the specified index.
        """
        return self._list[i]

    def __setitem__(self, i : int, v : T) -> None:
        """
        Set an item in the list by index.
        Args:
            i (int): Index of the item.
            v (object): Value to set.
        Raises:
            RuntimeError: If the list is frozen.
        """
        if self.frozen_list:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")
        self._list[i] = v

    def __delitem__(self, i : int) -> None:
        """
        Delete an item from the list by index.
        Args:
            i (int): Index of the item.
        Raises:
            RuntimeError: If the list is frozen.
        """
        if self.frozen_list:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")
        del self._list[i]

    def insert(self, index, value : T) -> None:
        """
        Insert an item into the list at a specific index.
        Args:
            i (int): Index to insert at.
            v (object): Value to insert.
        Raises:
            RuntimeError: If the list is frozen.
        """
        if self.frozen_list:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")
        self._list.insert(index, value)

    def __len__(self) -> int:
        """
        Get the length of the list.
        Returns:
            int: The number of items in the list.
        """
        return len(self._list)

    def __iter__(self) -> Iterator[T]:
        """
        Get an iterator for the list.
        Returns:
            iterator: An iterator for the list.
        """
        return iter(self._list)

    def __contains__(self, m : T) -> bool:
        """
        Check if an item is in the list.
        Args:
            m (object): The item to check.
        Returns:
            bool: True if the item is in the list, False otherwise.
        """
        return m in self._list


    # List utilities
    def replace(self, other_list : List[T]) -> None:
        """
        Replace the contents of this list with another list.
        Args:
            other_list (list): The list to copy from.
        Raises:
            RuntimeError: If the list is frozen.
        """
        if self.frozen_list:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")

        self._list = list(other_list)


    # Freezing
    def freeze_list(self, freeze:bool=True, *, recursive:bool=False, temporary:bool=False) -> None:
        """
        Freeze or unfreeze the list (optionally recursively or temporarily).
        Args:
            freeze (bool): If True, freeze the list.
            recursive (bool): If True, apply recursively to contained objects.
            temporary (bool): If True, use a context manager for temporary freezing.
        Returns:
            EnterExitCall or None: Context manager if temporary, else None.
        """
        if temporary:
            return EnterExitCall(
                self.freeze_list, self.freeze_list,
                kwargs_enter={'freeze': freeze, 'recursive': recursive, 'temporary': False},
                kwargs_exit={'freeze': not freeze, 'recursive': recursive, 'temporary': False})

        if recursive:
            for obj in self.__values():
                if hasattr(obj, 'frozen_list') and obj.frozen_list != freeze and callable(getattr(obj, 'freeze_list', None)):
                    obj.freeze_list(freeze=freeze, recursive=True, temporary=False)

        self.__frozen_list = freeze

    def unfreeze_list(self, recursive:bool=False, temporary:bool=False) -> None:
        """
        Unfreeze the list (optionally recursively or temporarily).
        Args:
            recursive (bool): If True, apply recursively.
            temporary (bool): If True, use a context manager for temporary unfreezing.
        Returns:
            EnterExitCall or None: Context manager if temporary, else None.
        """
        return self.freeze_list(False, recursive=recursive, temporary=temporary)

    @property
    def frozen_list(self):
        """
        Check if the list is currently frozen.
        Returns:
            bool: True if frozen, False otherwise.
        """
        return self.__frozen_list
    @frozen_list.setter
    def frozen_list(self, val:bool):
        """
        Set the frozen state of the list.
        Args:
            val (bool): True to freeze, False to unfreeze.
        """
        self.freeze_list(val, temporary=False)


    # Printing
    def aslist(self, recursive:bool=True, private:bool=False, protected:bool=True, public:bool=True) -> List[T]:
        """
        Convert the NamespaceList to a list, optionally recursively.
        Args:
            recursive (bool): If True, convert contained objects recursively.
            private (bool): Include private attributes.
            protected (bool): Include protected attributes.
            public (bool): Include public attributes.
        Returns:
            list: The list representation.
        """
        if not recursive:
            return list(self._list)

        l = []
        for v in self._list:

            if isinstance(v, Namespace):
                v = v.asdict(recursive=recursive, private=private, protected=protected, public=public)

            if not private and is_dataclass(v) and not isinstance(v, type):
                v = dataclass_asdict(v)

            l.append(v)

        return l

    def asdict(self, recursive:bool=True, private:bool=False, protected:bool=True, public:bool=True) -> Dict[str, Any]:
        """
        Convert the NamespaceList to a dictionary, optionally recursively.
        Args:
            recursive (bool): If True, convert contained objects recursively.
            private (bool): Include private attributes.
            protected (bool): Include protected attributes.
            public (bool): Include public attributes.
        Returns:
            dict: The dictionary representation.
        """
        d = super().asdict(recursive=recursive, private=private, protected=protected, public=public)

        if not recursive:
            return d

        d['_list'] = self.aslist(recursive=recursive, private=private, protected=protected, public=public)
        return d




    def __repr__(self) -> str:
        """
        Get the string representation of the NamespaceList.

        Returns:
            str: The string representation.
        """
        return f"<{self._Namespace__repr_name}:{repr(self.aslist(recursive=False))}>"
