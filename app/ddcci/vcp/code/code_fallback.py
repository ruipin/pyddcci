# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Any

from ..storage import FallbackVcpStorageStorable, T_VcpStorageIdentifier, T_VcpStorageName

from .code_storage import VcpCodeStorage
from .code import VcpCode


class FallbackVcpCode(FallbackVcpStorageStorable):
    def __init__(self, identifier : T_VcpStorageIdentifier, parent : VcpCodeStorage):
        super().__init__(identifier, parent)

    def get_wrapped_storable(self, check_fallback=True) -> VcpCode:
        return self.instance_parent.get(self._identifier, check_fallback=check_fallback, wrap_fallback=False)

    def create_wrapped_storable(self):
        storable = self.get_wrapped_storable()

        res = self.instance_parent.add(storable.vcp_storage_key())
        res._names = storable._names
        return res

    def _wrap_method_return_value(self, value: Any) -> Any:
        from ..value import VcpValue
        if isinstance(value, VcpValue):
            from ..value import FallbackVcpValue
            return FallbackVcpValue(value.name, self)
        else:
            return value

FallbackVcpCode.wrap_storable_class(FallbackVcpCode, VcpCode)
