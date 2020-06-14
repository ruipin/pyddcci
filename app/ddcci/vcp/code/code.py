# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, Dict, Any

from ..enums import VcpControlType
from ..storage import VcpStorageStorable, T_VcpStorageIdentifier, T_VcpStorageName, T_VcpStorageKey

from app.util import Namespace, HierarchicalMixin, NamedMixin


class VcpCode(VcpStorageStorable, HierarchicalMixin, NamedMixin):
    def __init__(self, code : int, instance_parent: HierarchicalMixin = None):
        super().__init__(instance_name=f"VcpCode0x{code:X}", instance_parent=instance_parent)

        self.code = code

        from ..value import VcpValueStorage
        self._values = VcpValueStorage(instance_name='values', instance_parent=self)

        self.type        = None
        self.description = None
        self.category    = None


    # Code
    def vcp_storage_key(self):
        return self.code
    def vcp_storage_key_name(self):
        return 'code'


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


    # Copying
    def copy_storable(self, other : 'VcpCode') -> None:
        super().copy_storable(other)

        self.type        = other.type
        self.description = other.description
        self.category    = other.category

        self.values.copy_storage(other.values)


    # Conversion
    def asdict(self, recursive=True, **kwargs) -> Dict[str, Any]:
        d = super().asdict(**kwargs)

        if recursive:
            values = self.values.asdict()
            if len(values) > 0:
                d['values'] = values
        else:
            d['values'] = self.values

        return d


    # Import / Export
    def export(self, diff : 'VcpCode' = None) -> Dict[str, Any]:
        if diff is None:
            return self.asdict()

        d = self.asdict(recursive=False)
        d_diff = diff.asdict(recursive=False)
        res = {}

        for k, v in d.items():
            # Values are handled separately
            if k == 'values':
                values_d = v.export(diff=d_diff['values'] if 'values' in d_diff else None)
                if values_d is not None and len(values_d) != 0:
                    res[k] = values_d
                continue

            # None keys not present in the diff are omitted
            if k not in d_diff:
                if v is not None:
                    res[k] = v
                continue

            # Matching keys are omitted
            diff_v = d_diff[k]
            if diff_v != v:
                res[k] = v

        return res
