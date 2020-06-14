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
    monitor.codes.asdict()