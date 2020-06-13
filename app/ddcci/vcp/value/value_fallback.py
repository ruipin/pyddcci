# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Hashable

from ..storage import FallbackVcpStorageStorable
from ..code import VcpCodeStorage

from .value import VcpValue

class FallbackVcpValue(FallbackVcpStorageStorable):
    WRITE_METHODS = ()

    def __init__(self, name : Hashable, parent : VcpCodeStorage):
        super().__init__(name, parent)

    def get_wrapped_storable(self, check_fallback=True) -> VcpValue:
        from ..code.code_fallback import FallbackVcpCode
        if isinstance(self.instance_parent, FallbackVcpCode):
            obj = self.instance_parent.get_wrapped_storable(check_fallback=check_fallback).values
        else:
            obj = self.instance_parent

        return obj.get(self._name, check_fallback=check_fallback, wrap_fallback=False)

    def create_wrapped_storable(self):
        storable = self.get_wrapped_storable()

        from ..code.code_fallback import FallbackVcpCode
        if isinstance(self.instance_parent, FallbackVcpCode):
            obj = self.instance_parent.create_wrapped_storable().values
        else:
            obj = self.instance_parent

        return obj.set(self._name, storable.vcp_storage_key())


FallbackVcpValue.wrap_storable_class(FallbackVcpValue, VcpValue)