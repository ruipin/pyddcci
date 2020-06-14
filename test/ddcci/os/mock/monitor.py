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
        return \
            "(" \
                "prot(monitor)" \
                "type(LCD)" \
                f"model({self.info.monitor.model})" \
                "cmds(01 02 03 07 0C E3 F3)" \
                "vcp(" \
                     "02 04 05 08 10 12 " \
                     "14(05 06 08 0B) " \
                     "16 18 1A 52 " \
                     "60(0F 10 11 12) " \
                     "62 " \
                     "72(50 78 96) " \
                     "86(02 0B) " \
                     "8A " \
                     "8D(01 02) " \
                     "95 96 97 98 AC AE B6 C6 C8 " \
                     "CC(01 02 03 04 05 06 07 08 09 0A 0C 0D 11 12 14 1A 1E 1F 23 30 31) " \
                     "D6(01 04 05) " \
                     "DC(03 0B 0D 0E 11 12 13 14) " \
                     "DF " \
                     "E2(00 01 02 03 04 05) " \
                     "E4(00 01) " \
                     "E6(00 01) " \
                     "E9(00 01) " \
                     "EA(00 01) " \
                     "EB(00 01) " \
                     "EC(00 01 02 03 04 05 06) " \
                     "EE(00 1E 28 32 3C 5A) " \
                     "EF(00 01 02 03) " \
                     "F0(00 01 02 03 04) " \
                     "F2(01 02) " \
                     "F3(00 01) " \
                     "F4(00 01) " \
                     "F6(00 01 02) " \
                ")" \
                "mswhql(1)" \
                "asset_eep(40)" \
                "mccs_ver(2.2)" \
            ")"

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
