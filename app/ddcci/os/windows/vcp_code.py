# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, Dict, Any, Optional

from .monitor import WindowsOsMonitor
from .. import BaseOsVcpCode
from ..vcp_code import VcpQuery, VcpCodeType

from . import Namespace, Sequence, getLogger

log = getLogger(__name__)


class WindowsOsVcpCode(BaseOsVcpCode):
    """
    Windows implementation of BaseOsVcpCode
    """

    __slots__ = Namespace.__slots__

    # Read
    def _read(self, monitor : WindowsOsMonitor) -> VcpQuery:
        with monitor.get_physical_handle() as physical:
            result = physical.query_vcp(self.command)

            if result['type'] == 0:
                typ = VcpCodeType.VCP_MOMENTARY
            elif result['type'] == 1:
                typ = VcpCodeType.VCP_SET_PARAMETER
            else:
                raise RuntimeError(f"Invalid VcpCodeType '{result['typ']}'")

            return VcpQuery(self, typ=typ, value=result['current'], maximum=result['maximum'])


    # Write
    def _write(self, monitor : WindowsOsMonitor, value : int) -> None:
        with monitor.get_physical_handle() as physical:
            physical.set_vcp(self.command, value)
