# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Any

from . import Namespace

from .. import LoggableMixin, HierarchicalMixin, NamedMixin
from ..enter_exit_call import EnterExitCall


class NamespaceMap(Namespace):
    """
    Class implementing a namespace that can be accessed like a dictionary or using attributes
    """

    # We want to hide some attributes from the dictionary
    # NOTE: We include the log/parent attributes here just in case someone decides to make this class Loggable or Hierarchical
    __slots__ = {'_NamespaceMap__frozen_map', '__dict__'}

    # Constructor
    def __init__(self, *, frozen_schema=False, frozen_map=False, **kwargs):
        # Call super-class
        super_params = {'frozen_schema': frozen_schema}
        if isinstance(self, NamedMixin):
            super_params['instance_name'] = kwargs.pop('instance_name', None)
        if isinstance(self, HierarchicalMixin):
            super_params['instance_parent'] = kwargs.pop('instance_parent', None)
        super().__init__(**super_params)

        # Initialize basic state before calling super constructors
        self.__frozen_map = False

        self.__dict__ = {}

        # Finish initialization
        self.merge(kwargs)

        self.__frozen_map = frozen_map


    # Accesses
    def _sanity_check_key(self, key : str, *, delete: bool =False) -> bool:
        pass

    def _Namespace__sanity_check_key(self, key : str, *, delete: bool =False) -> None:
        super()._Namespace__sanity_check_key(key, delete=delete)

        if key and key[0] != '_':
            self._sanity_check_key(key, delete=delete)

    def _Namespace__is_slots_key(self, key : str) -> bool:
        return key in NamespaceMap.__slots__ or super()._Namespace__is_slots_key(key)

    def _Namespace__get_access_dict(self, key: str) -> dict:
        if key and key[0] != '_':
            return self.__dict__
        else:
            return super()._Namespace__get_access_dict(key)


    # Write Accesses
    def _get_write_target(self, key : str) -> 'Namespace':
        return self

    def _Namespace__get_write_target(self, key : str) -> 'Namespace':
        if key and key[0] == '_':
            return self
        else:
            return self._get_write_target(key)

    def _Namespace__is_frozen_key(self, key : str) -> bool:
        if super()._Namespace__is_frozen_key(key):
            return True

        if self.frozen_map and self._get_access_dict(key) is self.__dict__:
            return True

        return False


    # Read accesses
    def get(self, key : str, default=Namespace.NO_DEFAULT):
        return self._Namespace__get(key, default=default)

    def _get_read_target(self, key):
        return self

    def _Namespace__get_read_target(self, key):
        if key and key[0] == '_':
            return self
        else:
            return self._get_read_target(key)


    # Iteration
    def __iter__(self):
        """ Returns an iterator to the internal dictionary """
        return iter(self.__dict__)

    def __len__(self):
        """ Returns the length of the internal dictionary """
        return len(self.__dict__)

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def values(self):
        return self.__dict__.values()


    # Comparison
    def __eq__(self, other):
        return self is other
        # return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)
        # return hash(self) != hash(other)

    def __hash__(self):
        """ Calculates a hash of the internal dictionary """
        return hash(self.__dict__)


    # Freezing
    def freeze_map(self, freeze=True, /, recursive=False, temporary=False):
        """ Freezes this object, so new attributes cannot be added """
        if temporary:
            return EnterExitCall(
                self.freeze_schema, self.freeze_schema,
                kwargs_enter={'freeze': freeze, 'recursive': recursive, 'temporary': False},
                kwargs_exit={'freeze': not freeze, 'recursive': recursive, 'temporary': False})

        if recursive:
            for obj in self.values():
                if hasattr(obj, 'frozen_map') and obj.frozen_map != freeze:
                    obj.freeze_map(freeze, recursive=True, temporary=False)

        if freeze and not self.frozen_schema:
            self.freeze_schema(True, recursive=False, temporary=False)

        self.__frozen_map = freeze

    def unfreeze_map(self, recursive=False, temporary=False):
        return self.freeze_map(False, recursive=recursive, temporary=temporary)


    @property
    def frozen_map(self):
        return self.__frozen_map
    @frozen_map.setter
    def frozen_map(self, val):
        self.freeze_map(val, temporary=False)


    # Utilities
    def asdict(self, recursive=True):
        if not recursive:
            return dict(self.__namespace)

        d = {}
        for k, v in self._dict.items():
            if isinstance(v, Namespace):
                v = v.to_dict(recursive=recursive)
            d[k] = v
        return d

    def merge(self, d):
        for k, v in d.items():
            self[k] = v


    # Printing
    def __repr__(self):
        return f"<{self._Namespace__repr_name}{repr(self.__dict__)}>"
