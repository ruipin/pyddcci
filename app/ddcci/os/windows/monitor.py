# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from .api.physical_monitor import OsMonitorPhysicalHandle
from ..monitor import BaseOsMonitor
from app.ddcci.vcp.enums import VcpCodeType
from app.ddcci.vcp.reply import VcpReply


##########
# OS Monitor class
class WindowsOsMonitor(BaseOsMonitor):
    """
    Windows implementation of BaseOsMonitor
    """

    # Physical Monitor Handle
    def get_physical_handle(self) -> OsMonitorPhysicalHandle:
        return OsMonitorPhysicalHandle(self)

    # Capabilities
    def _get_capabilities_string(self) -> str:
        with self.get_physical_handle() as physical:
            return physical.get_capabilities_string()


    # VCP Query
    def _vcp_query(self, code: int) -> VcpReply:
        with self.get_physical_handle() as physical:
            result = physical.query_vcp(code)

            if result['type'] == 0:
                typ = VcpCodeType.VCP_MOMENTARY
            elif result['type'] == 1:
                typ = VcpCodeType.VCP_SET_PARAMETER
            else:
                raise RuntimeError(f"Invalid VcpCodeType '{result['typ']}'")

            return VcpReply(code, type=typ, current=result['current'], maximum=result['maximum'])

    # VCP Write
    def _vcp_write(self, code: int, value: int) -> None:
        with self.get_physical_handle() as physical:
            physical.set_vcp(code, value)
