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
    CFG.debug(user_only=True)
