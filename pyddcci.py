# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import sys
from app.util import CFG, getLogger
import yaml


if __name__ == "__main__":
    log = getLogger(CFG.app.name)

    log.info("Starting.")
    log.debug('Cmdline= %s', ' '.join(sys.argv))
    CFG.debug()


    from app.ddcci.monitor import Monitor
    monitor = Monitor('Primary')

    monitor['input'] = 'dp1'

    prev = monitor['input']
    log.info(f"Previous Input: {prev}")

    monitor['input'] = 'HDMI 1'
    log.info(f"Switched to {monitor['input']}")

    monitor['input'] = prev
    log.info(f"Back to {monitor['input']}")