# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Any, Dict, Union, Optional

from .value import VcpValue
from ..storage import VcpStorage, T_VcpStorageIdentifier


class VcpValueStorage(VcpStorage):
    """
    Storage for VcpValue objects, providing methods to add, retrieve, and manage VCP values.
    Used for storing possible values for a given VCP code.
    """
    def _create_value(self, value : int) -> VcpValue:
        return VcpValue(value, instance_parent=self)