# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from app.ddcci.os.monitor import BaseOsMonitor
from app.ddcci.vcp.reply import VcpReply


##########
# OS Monitor class
class MockOsMonitor(BaseOsMonitor):
    """
    Windows implementation of BaseOsMonitor
    """

    # Capabilities
    def _get_capabilities_string(self) -> str:
        raise NotImplementedError()


    # VCP Query
    def _vcp_query(self, code: int) -> VcpReply:
        raise NotImplementedError()

    # VCP Write
    def _vcp_write(self, code: int, value: int) -> None:
        raise NotImplementedError()


WindowsOsMonitor = MockOsMonitor