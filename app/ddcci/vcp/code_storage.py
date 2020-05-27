# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Any

from .code import VcpCode
from .storage import VcpStorage


class VcpCodeStorage(VcpStorage):
    def _is_value(self, obj : Any) -> bool:
        return isinstance(obj, VcpCode)

    def _create_value(self, code : int) -> VcpCode:
        return VcpCode(code, parent=self)