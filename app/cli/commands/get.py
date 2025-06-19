# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Any

from . import CliCommand, FilterCliCommandMixin, CodeCliCommandMixin

class GetCliCommand(FilterCliCommandMixin, CodeCliCommandMixin, CliCommand):
    """
    CLI command to get a VCP code value from a monitor.
    Supports raw and formatted output.
    """
    def __init__(self, *args, raw : bool = False, **kwargs):
        """
        Initialize the GetCliCommand.
        Args:
            raw: If True, output the raw VCP code value.
        """
        super().__init__(*args, **kwargs)

        self.raw = raw

    @classmethod
    def constructor_args_from_argparse(cls, *args, raw : bool, **kwargs) -> Dict[str, Any]:
        """
        Build constructor arguments from argparse for this command.
        Args:
            raw: If True, output the raw VCP code value.
        Returns:
            dict: Constructor arguments.
        """
        d = super(GetCliCommand, cls).constructor_args_from_argparse(*args, **kwargs)

        d['raw'] = raw

        return d


    # Execute
    def execute(self) -> None:
        """
        Execute the get command: read and print the VCP value from the monitor.
        """
        value = self.monitor.vcp_read(self.code)

        if self.raw:
            print(value.value)
        else:
            print(value)

CliCommand.CLI_COMMAND_TYPES['get'] = GetCliCommand