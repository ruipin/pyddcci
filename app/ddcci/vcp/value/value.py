# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Union, Optional
from ordered_set import OrderedSet

from ..storage import VcpStorageStorable

from app.util import HierarchicalMixin, NamedMixin


class VcpValue(VcpStorageStorable['VcpValue'], HierarchicalMixin, NamedMixin):
    """
    Represents a valid value for a given VcpCode, including its integer value and name aliases.
    Supports serialization and deserialization for configuration and communication.

    Args:
        value: The integer value for this VCP value.
        instance_parent: Optional parent for hierarchy.
    """

    def __init__(self, value : int, instance_parent : HierarchicalMixin):
        super().__init__(instance_name=fr"VcpValue0x{value:X}", instance_parent=instance_parent)

        self._value = value
        self._names = OrderedSet() # type: ignore - OrderedSet can indeed be used with empty parameters


    # Value
    @property
    def value(self):
        """
        Get the integer value for this VCP value.

        Returns:
            int: The value.
        """
        return self._value

    def vcp_storage_key(self):
        """
        Return the integer key for storage (the value).

        Returns:
            int: The value.
        """
        return self._value

    def vcp_storage_key_name(self):
        """
        Return the name of the storage key ("value").

        Returns:
            str: The key name.
        """
        return 'value'


    # Import / Export
    def serialize(self, diff : 'VcpValue|None' = None) -> Union[Dict, str]: # type: ignore - changing 'diff' type to VcpValue on purpose
        """
        Serialize this VcpValue, optionally as a diff from another VcpValue.

        Args:
            diff: Optional VcpValue to diff against.

        Returns:
            dict or str: The serialized representation.
        """
        if diff is None:
            res = self.asdict()

        else:
            if not isinstance(diff, VcpValue):
                raise TypeError(f"Expected VcpValue for diff parameter, got {type(diff).__name__}")

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

    def deserialize(self, data : Union[Dict, str], diff : Optional['VcpValue'] = None) -> None: # type: ignore - changing 'diff' type to VcpValue on purpose
        """
        Deserialize this VcpValue from a dictionary or string, optionally using a diff.

        Args:
            data: The data to deserialize from.
            diff: Optional diff VcpValue.
        """
        if isinstance(data, str):
            data = {'name': data}

        self._fromdict(data)

        if diff is not None:
            if not isinstance(diff, VcpValue):
                raise TypeError(f"Expected VcpValue for diff parameter, got {type(diff).__name__}")
            if not self.has_name:
                self.add_names(*diff.names)