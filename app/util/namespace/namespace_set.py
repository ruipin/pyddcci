# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta
from collections.abc import MutableSet
from ordered_set import OrderedSet
from dataclasses import is_dataclass, asdict as dataclass_asdict

from .namespace import Namespace
from ..mixins import *
from ..enter_exit_call import EnterExitCall


class NamespaceSet(Namespace, MutableSet, metaclass=ABCMeta):
    """
    list wrapper with extended functionality
    """


    # Constructor
    def __init__(self, *args, frozen_schema=False, frozen_namespace=False, frozen_set=False, **kwargs):
        """ Initializes a list """

        # Call super-class
        super_params = {'frozen_schema': frozen_schema, 'frozen_namespace': frozen_namespace}
        if isinstance(self, LoggableMixin):
            super_params['instance_name'] = kwargs.pop('instance_name', None)
        if isinstance(self, HierarchicalMixin):
            super_params['instance_parent'] = kwargs.pop('instance_parent', None)
        super().__init__(**super_params)

        self.__frozen_set   = False

        self._set = OrderedSet(*args, **kwargs)

        self.__frozen_set = frozen_set


    # Abstract methods implementation
    def add(self, m):
        if self.frozen_set:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")
        self._set.add(m)

    def discard(self, m):
        if self.frozen_set:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")
        self._set.discard(m)

    def __len__(self):
        return len(self._set)

    def __iter__(self):
        return iter(self._set)

    def __contains__(self, m):
        return m in self._set


    # Set utilities
    def replace(self, other_set):
        if self.frozen_set:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")

        self._set = set(other_set)


    # Freezing
    def freeze_set(self, freeze=True, *, recursive=False, temporary=False):
        """ Freezes this object, so new attributes cannot be added """
        if temporary:
            return EnterExitCall(
                self.freeze_set, self.freeze_set,
                kwargs_enter={'freeze': freeze, 'recursive': recursive, 'temporary': False},
                kwargs_exit={'freeze': not freeze, 'recursive': recursive, 'temporary': False})

        if recursive:
            for obj in self.values():
                if hasattr(obj, 'frozen_set') and obj.frozen_set != freeze:
                    obj.freeze_set(freeze=freeze, recursive=True, temporary=False)

        self.__frozen_set = freeze

    def unfreeze_set(self, recursive=False, temporary=False):
        return self.freeze_set(False, recursive=recursive, temporary=temporary)

    @property
    def frozen_set(self):
        return self.__frozen_set
    @frozen_set.setter
    def frozen_set(self, val):
        self.freeze_set(val, temporary=False)


    # Printing
    def asset(self, recursive=True, private=False, protected=True, public=True):
        if not recursive:
            return set(self._set)

        s = set()
        for v in self._set:

            if isinstance(v, Namespace):
                v = v.asdict(recursive=recursive, private=private, protected=protected, public=public)

            if not private and is_dataclass(v) and not isinstance(v, type):
                v = dataclass_asdict(v)

            s.add(v)

        return s

    def asdict(self, recursive=True, private=False, protected=True, public=True):
        d = super().asdict(recursive=recursive, private=private, protected=protected, public=public)

        if not recursive:
            return d

        d['_set'] = self.asset(recursive=recursive, private=private, protected=protected, public=public)
        return d




    def __repr__(self):
        return f"<{self._Namespace__repr_name}:{repr(self.asset(recursive=False))}>"
