# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import sys
import time
from app.util import CFG, getLogger


# app
# from app.x import y

from app.util import LoggableMixin, HierarchicalMixin, NamedMixin, Namespace

if __name__ == "__main__":
    log = getLogger(CFG.app.name)

    log.info("Starting.")
    log.debug('Cmdline= %s', ' '.join(sys.argv))
    CFG.debug()

    #from app.ddcci.monitor import OS_MONITORS
    #print()
    #log.debug(repr(OS_MONITORS))
    #print()
    #OS_MONITORS.enumerate()
    #log.debug(repr(OS_MONITORS))


    #from app.ddcci.monitor import Monitor
    #monitor = Monitor('Primary')
    #contrast = monitor.vcp_read_raw(0x12)
    #print(f"Current Contrast: {contrast}")
    #monitor.vcp_write_raw(0x12, 20)
    #time.sleep(1)
    #monitor.vcp_write_raw(0x12, contrast)

    #print()
    #log.debug(f"VCP Code Capabilities: {repr(monitor.get_os_monitor().capabilities.get_vcp_codes())}")

    print()
    from app.ddcci.vcp.code_storage import VcpCodeStorage
    codes = VcpCodeStorage()

    contrast = codes.set("Constrast", 0x12)
    log.debug(f"Contrast: {contrast}")
    print(contrast.aliases)

    contrast.aliases.set("50PCT", 50)
    contrast.aliases.set("20PCT", 20)
    contrast.aliases.set("HALF", 50)
    print(contrast.aliases)
    fifty = contrast.aliases['50PCT']
    fifty.add_name("FIFTY")
    log.debug(f"50PCT: {fifty}")
    log.debug(f"Names: {fifty.names}")
    log.debug(f"FIFTY: {contrast.aliases['FIFTY']}")

    #print()
    #import time
    #from app.ddcci.os import OsVcpCode
    #code = OsVcpCode(0x12)
    #query = code.read(monitor)
    #log.debug(repr(query))
    #code.write(monitor, 10)
    #time.sleep(1)
    #code.write(monitor, query.value)