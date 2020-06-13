# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Hashable, Any

from ..storage.fallback_storable import FallbackVcpStorageStorable

from .code_storage import VcpCodeStorage
from .code import VcpCode


class FallbackVcpCode(FallbackVcpStorageStorable):
    def __init__(self, name : Hashable, parent : VcpCodeStorage):
        super().__init__(name, parent)

    def get_wrapped_storable(self, check_fallback=True) -> VcpCode:
        return self.instance_parent.get(self._name, check_fallback=check_fallback, wrap_fallback=False)

    def create_wrapped_storable(self):#
        storable = self.get_wrapped_storable()
        return self.instance_parent.set(self._name, storable.vcp_storage_key())

    def _wrap_method_return_value(self, value: Any) -> Any:
        from ..value import VcpValue
        if isinstance(value, VcpValue):
            from ..value import FallbackVcpValue
            return FallbackVcpValue(value.name, self)
        else:
            return value

FallbackVcpCode.wrap_storable_class(FallbackVcpCode, VcpCode)