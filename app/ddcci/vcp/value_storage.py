# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Any

from .value import VcpValue
from .storage import VcpStorage


class VcpValueStorage(VcpStorage):
    def _is_storable_value(self, obj : Any) -> bool:
        return isinstance(obj, VcpValue)

    def _create_value(self, value : int) -> VcpValue:
        return VcpValue(value, instance_parent=self)
