# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import sys
import time
from app import CFG, getLogger


# app
# from app.x import y


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


    from app.ddcci.monitor import Monitor
    monitor = Monitor('Primary')

    #print()
    #log.debug(monitor)

    #print()
    #log.debug(f"VCP Code Capabilities: {repr(monitor.get_os_monitor().capabilities.get_vcp_codes())}")

    contrast = monitor.vcp_read_raw(0x12)
    print(f"Current Contrast: {contrast}")

    monitor.vcp_write_raw(0x12, 20)

    time.sleep(1)

    monitor.vcp_write_raw(0x12, contrast)

    #print()
    #import time
    #from app.ddcci.os import OsVcpCode
    #code = OsVcpCode(0x12)
    #query = code.read(monitor)
    #log.debug(repr(query))
    #code.write(monitor, 10)
    #time.sleep(1)
    #code.write(monitor, query.value)