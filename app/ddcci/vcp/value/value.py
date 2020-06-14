# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Union, Optional
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
    def serialize(self, diff : 'VcpValue' =None) -> Union[Dict, str]:
        if diff is None:
            res = self.asdict()

        else:
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

        if 'name' in res and len(res) == 1:
            res = res['name']

        return res

    def deserialize(self, data : Union[Dict, str], diff : Optional['VcpValue'] = None) -> None:
        if isinstance(data, str):
            data = {'name': data}

        self._fromdict(data)

        if diff is not None:
            if not self.has_name:
                self.add_names(*diff.names)