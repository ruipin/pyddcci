# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import sys
from app import CFG, getLogger


# app
# from app.x import y


if __name__ == "__main__":
    log = getLogger(CFG.app.name)

    log.info("Starting.")
    log.debug('Cmdline= %s', ' '.join(sys.argv))
    CFG.debug()

    from app.ddcci.monitor import OS_MONITORS
    print()

    log.debug(repr(OS_MONITORS))
    print()

    OS_MONITORS.enumerate()
    log.debug(repr(OS_MONITORS))
