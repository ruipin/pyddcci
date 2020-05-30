# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, Hashable, Set, Iterable

from ordered_set import OrderedSet

from .enums import VcpControlType
from .storage import VcpStorageStorable
from .value_storage import VcpValueStorage
from .value import VcpValue

from app.util import Namespace, HierarchicalMixin, NamedMixin


class VcpCode(VcpStorageStorable, Namespace, HierarchicalMixin, NamedMixin):
    def __init__(self, code : int, instance_parent: HierarchicalMixin = None):
        super().__init__(instance_name=f"VcpCode0x{code:X}", instance_parent=instance_parent)

        self.code = code

        self._values = VcpValueStorage(instance_parent=self)

        self.type = None
        self.description = None
        self.category = None
        self.verify = False

        self.freeze_schema()


    # Code
    def vcp_storage_key(self):
        return self.code


    # Type
    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, new_type : Union[None, VcpControlType]):
        self._type = new_type


    # Aliases
    @property
    def values(self):
        return self._values

    def add_value(self, new_value_name : Hashable, new_value : int):
        self._values[new_value_name] = new_value



    # Magic methods (wrap Value Storage)
    def __getitem__(self, key : Hashable):
        """ Get an attribute using dictionary syntax obj[key] """
        return self.values.get(key)

    def __setitem__(self, key : Hashable, value : int):
        """ Modify an attribute using dictionary syntax obj[key] = value """
        self.values.set(key, value)

    def __delitem__(self, key : Hashable):
        """ Delete an attribute using dictionary syntax """
        self.values.remove(key)

    def __contains__(self, key : Hashable):
        return self.values.contains(key)
