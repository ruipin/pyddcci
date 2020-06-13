# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, Hashable

from ..enums import VcpControlType
from ..storage.storable import VcpStorageStorable
from ..storage.storage_with_fallback import VcpStorageWithFallback

from app.util import Namespace, HierarchicalMixin, NamedMixin


class VcpCode(VcpStorageStorable, Namespace, HierarchicalMixin, NamedMixin):
    WRITE_METHODS = ('add_value', 'type', '__setitem__', '__delitem__')

    def __init__(self, code : int, instance_parent: HierarchicalMixin = None):
        super().__init__(instance_name=f"VcpCode0x{code:X}", instance_parent=instance_parent)

        self.code = code

        from ..value import VcpValueStorage
        self._values = VcpValueStorage(instance_name='values', instance_parent=self)
        if isinstance(self.instance_parent, VcpStorageWithFallback) and self.instance_parent.fallback is not None:
            self._values.fallback = self.instance_parent.fallback

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
    def add_value(self, new_value_name : Hashable, new_value : int):
        self._values[new_value_name] = new_value



    # Magic methods (wrap Value Storage)
    def __getitem__(self, key : Hashable):
        """ Get an attribute using dictionary syntax obj[key] """
        return self._values.get(key)

    def __setitem__(self, key : Hashable, value : int):
        """ Modify an attribute using dictionary syntax obj[key] = value """
        self._values.set(key, value)

    def __delitem__(self, key : Hashable):
        """ Delete an attribute using dictionary syntax """
        self._values.remove(key)

    def contains(self, name : Hashable):
        return self._values.contains(name)

    def __contains__(self, key : Hashable):
        return self.contains(key)
