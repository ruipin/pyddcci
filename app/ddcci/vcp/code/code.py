# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, Dict, Any

from ..enums import VcpControlType
from ..storage import VcpStorageStorable, T_VcpStorageIdentifier, T_VcpStorageName, T_VcpStorageKey
from ..storage.storage_with_fallback import VcpStorageWithFallback

from app.util import Namespace, HierarchicalMixin, NamedMixin


class VcpCode(VcpStorageStorable, HierarchicalMixin, NamedMixin):
    WRITE_METHODS = ('add_value', 'type', '__setitem__', '__delitem__', 'values')

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


    # Code
    def vcp_storage_key(self):
        return self.code
    def vcp_storage_key_name(self):
        return 'code'


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
    def add_value(self, name : T_VcpStorageName, new_value : T_VcpStorageKey):
        self._values[name] = new_value



    # Magic methods (wrap Value Storage)
    def __getitem__(self, identifier : T_VcpStorageIdentifier):
        """ Get an attribute using dictionary syntax obj[key] """
        return self._values.get(identifier)

    def __setitem__(self, identifier : T_VcpStorageIdentifier, value : T_VcpStorageKey):
        """ Modify an attribute using dictionary syntax obj[key] = value """
        self._values.set(identifier, value)

    def __delitem__(self, identifier : T_VcpStorageIdentifier):
        """ Delete an attribute using dictionary syntax """
        self._values.remove(identifier)

    def contains(self, identifier : T_VcpStorageIdentifier):
        return self._values.contains(identifier)

    def __contains__(self, identifier : T_VcpStorageIdentifier):
        return self.contains(identifier)


    # Conversion
    def asdict(self) -> Dict[str, Any]:
        d = super().asdict()
        d['values'] = self.values.asdict()
        return d
