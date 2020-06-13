# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from app.ddcci.os.monitor import BaseOsMonitor
from app.ddcci.vcp.reply import VcpReply

from app.ddcci.vcp.enums import VcpCodeType


##########
# OS Monitor class
class MockOsMonitor(BaseOsMonitor):
    """
    Mock implementation of BaseOsMonitor
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.codes = {}

    # Capabilities
    def _get_capabilities_string(self) -> str:
        raise NotImplementedError()


    # VCP Query
    def _vcp_query(self, code: int) -> VcpReply:
        self.log.debug(f"MOCK: _vcp_query(0x{code:X})")
        reply = VcpReply(
            command = code,
            type    = VcpCodeType.VCP_SET_PARAMETER,
            current = self.codes.get(code, 0),
            maximum = 255
        )
        return reply

    # VCP Write
    def _vcp_write(self, code: int, value: int) -> None:
        self.log.debug(f"MOCK: _vcp_write(0x{code:X}, 0x{value:X})")
        self.codes[code] = value
        return


WindowsOsMonitor = MockOsMonitor
