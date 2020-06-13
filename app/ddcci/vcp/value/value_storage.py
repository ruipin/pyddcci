# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Any, Hashable

from .value import VcpValue
from .value_fallback import FallbackVcpValue
from ..storage import VcpStorageWithFallback


class VcpValueStorage(VcpStorageWithFallback):
    def _is_storable_value(self, obj : Any) -> bool:
        return isinstance(obj, VcpValue)

    def _create_value(self, value : int) -> VcpValue:
        return VcpValue(value, instance_parent=self)

    def _get_fallback(self) -> VcpStorageWithFallback:
        return self._fallback if hasattr(self, '_fallback') else None

    def _set_fallback(self, new_fallback: VcpStorageWithFallback) -> None:
        self._fallback = new_fallback

    def _get_fallback_storage(self) -> 'VcpValueStorage':
        from ..code import VcpCode
        if not isinstance(self.instance_parent, VcpCode):
            raise RuntimeError('_get_fallback_storage: self.instance_parent must be of class VcpCode')

        return self.fallback.get(self.instance_parent.vcp_storage_key(), check_fallback=True).values

    def _wrap_fallback_storable(self, name : Hashable, storable : VcpValue) -> 'FallbackVcpValue':
        return FallbackVcpValue(name, self.instance_parent)
