# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Any
from ordered_set import OrderedSet

from ..storage import VcpStorageStorable

from app.util import HierarchicalMixin, NamedMixin


class VcpValue(VcpStorageStorable, HierarchicalMixin, NamedMixin):
    """
    Class that represents a valid value for a given VcpCode, including name aliases
    """

    def __init__(self, value : int, instance_parent : HierarchicalMixin):
        super().__init__(instance_name=fr"VcpValue0x{value:X}", instance_parent=instance_parent)

        self._value = value
        self._names = OrderedSet()


    # Value
    @property
    def value(self):
        return self._value

    def vcp_storage_key(self):
        return self._value
    def vcp_storage_key_name(self):
        return 'value'


    # Import / Export
    def export(self, diff : 'VcpValue' =None) -> Dict:
        if diff is None:
            return self.asdict()

        d = self.asdict()
        d_diff = diff.asdict()
        res = {}

        for k, v in d.items():
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
