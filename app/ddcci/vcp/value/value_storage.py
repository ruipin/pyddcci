# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Any, Dict, Union, Optional

from .value import VcpValue
from ..storage import VcpStorage


class VcpValueStorage(VcpStorage[VcpValue]):
    """
    Storage for VcpValue objects, providing methods to add, retrieve, and manage VCP values.
    Used for storing possible values for a given VCP code.
    """
    def _create_value(self, key : int) -> VcpValue:
        """
        Create a new VcpValue instance for the given value.
        Args:
            value: The integer value for the VCP value.
        Returns:
            VcpValue: The created VcpValue instance.
        """
        return VcpValue(key, instance_parent=self)