# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta
from collections import MutableSequence
from dataclasses import is_dataclass, asdict as dataclass_asdict

from .namespace import Namespace
from ..mixins import *
from ..enter_exit_call import EnterExitCall


class NamespaceList(Namespace, MutableSequence, metaclass=ABCMeta):
    """
    list wrapper with extended functionality
    """


    # Constructor
    def __init__(self, *args, frozen_schema=False, frozen_namespace=False, frozen_list=False, **kwargs):
        """ Initializes a list """

        # Call super-class
        super_params = {'frozen_schema': frozen_schema, 'frozen_namespace': frozen_namespace}
        if isinstance(self, LoggableMixin):
            super_params['instance_name'] = kwargs.pop('instance_name', None)
        if isinstance(self, HierarchicalMixin):
            super_params['instance_parent'] = kwargs.pop('instance_parent', None)
        super().__init__(**super_params)

        self.__frozen_list   = False

        self._list = list(*args, **kwargs)

        self.__frozen_list = frozen_list


    # Abstract methods implementation
    def __getitem__(self, i):
        return self._list[i]

    def __setitem__(self, i, v):
        if self.frozen_list:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")
        self._list[i] = v

    def __delitem__(self, i):
        if self.frozen_list:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")
        del self._list[i]

    def insert(self, i, v):
        if self.frozen_list:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")
        self._list.insert(i, v)

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return iter(self._list)

    def __contains__(self, m):
        return m in self._list


    # List utilities
    def replace(self, other_list):
        if self.frozen_list:
            raise RuntimeError(f"{self.__class__.__name__} is frozen")

        self._list = list(other_list)


    # Freezing
    def freeze_list(self, freeze=True, *, recursive=False, temporary=False):
        """ Freezes this object, so new attributes cannot be added """
        if temporary:
            return EnterExitCall(
                self.freeze_list, self.freeze_list,
                kwargs_enter={'freeze': freeze, 'recursive': recursive, 'temporary': False},
                kwargs_exit={'freeze': not freeze, 'recursive': recursive, 'temporary': False})

        if recursive:
            for obj in self.values():
                if hasattr(obj, 'frozen_list') and obj.frozen_list != freeze:
                    obj.freeze_list(freeze=freeze, recursive=True, temporary=False)

        self.__frozen_list = freeze

    def unfreeze_list(self, recursive=False, temporary=False):
        return self.freeze_list(False, recursive=recursive, temporary=temporary)

    @property
    def frozen_list(self):
        return self.__frozen_list
    @frozen_list.setter
    def frozen_list(self, val):
        self.freeze_list(val, temporary=False)


    # Printing
    def aslist(self, recursive=True, private=False, protected=True, public=True):
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

    def asdict(self, recursive=True, private=False, protected=True, public=True):
        d = super().asdict(recursive=recursive, private=private, protected=protected, public=public)

        if not recursive:
            return d

        d['_list'] = self.aslist(recursive=recursive, private=private, protected=protected, public=public)
        return d




    def __repr__(self):
        return f"<{self._Namespace__repr_name}:{repr(self._list)}>"
