# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Any

from .value import VcpValue
from .value_fallback import FallbackVcpValue
from ..storage import VcpStorageWithFallback, T_VcpStorageIdentifier


class VcpValueStorage(VcpStorageWithFallback):
    def _create_value(self, value : int) -> VcpValue:
        return VcpValue(value, instance_parent=self)

    def _get_fallback_storage(self) -> 'VcpValueStorage':
        from ..code import VcpCode
        if not isinstance(self.instance_parent, VcpCode):
            raise RuntimeError('_get_fallback_storage: self.instance_parent must be of class VcpCode')

        if self.fallback is None:
            return None

        return self.fallback.get(self.instance_parent.vcp_storage_key(), check_fallback=True)._values

    def _wrap_fallback_storable(self, identifier : T_VcpStorageIdentifier, storable : VcpValue) -> 'FallbackVcpValue':
        return FallbackVcpValue(identifier, self.instance_parent)
