# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Implements the CliCommands container for managing and executing CLI command objects.
Provides methods to populate from argparse and to execute all commands in sequence.
"""

from app.util import CFG
from app.util.mixins import LoggableMixin
from app.util.namespace import NamespaceList

from .commands.base import CliCommand

class CliCommands(NamespaceList, LoggableMixin):
    """
    Container for CLI command objects. Handles execution and population from argparse.
    """
    def execute(self):
        """
        Execute all CLI commands in the container, handling errors as configured.
        """
        for cmd in self:
            try:
                cmd.execute()
            except Exception as e:
                if CFG.app.cli.ignore_errors:
                    self.log.error(f"Error executing command '{cmd}': {repr(e)}.")
                else:
                    raise RuntimeError(f"Error executing command '{cmd}'") from e

    def from_argparse(self, argparse_commands=None):
        """
        Populate the container from parsed argparse command objects.
        """
        if argparse_commands is None:
            argparse_commands = CFG.app.cli.get('commands', None)

        if argparse_commands is None:
            return

        for argparse_command in argparse_commands:
            try:
                cmd_obj = CliCommand.from_argparse(argparse_command)
                self.append(cmd_obj)
            except Exception as e:
                if CFG.app.cli.ignore_errors:
                    self.log.error(f"Invalid command: {str(e)}.")
                else:
                    raise RuntimeError(f"Invalid command '{argparse_command}'") from e