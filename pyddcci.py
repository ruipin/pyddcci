# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import sys
from app.util import CFG, getLogger


if __name__ == "__main__":
    log = getLogger(CFG.app.name)

    log.debug('Cmdline= %s', ' '.join(sys.argv))
    CFG.debug()

    from app.cli.cli_commands import CliCommands
    cli_commands = CliCommands()
    cli_commands.from_argparse(CFG.app.cli.commands)
    cli_commands.execute()