# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Any

from . import CliCommand, FilterCliCommandMixin, CodeCliCommandMixin, ValuesCliCommandMixin

class MultiSetCliCommand(FilterCliCommandMixin, CodeCliCommandMixin, ValuesCliCommandMixin, CliCommand):
    """
    CLI command to set a VCP code to multiple values in sequence on a monitor.
    Supports optional verification after setting each value.
    """
    def __init__(self, *args, verify : bool = False, **kwargs):
        """
        Initialize the MultiSetCliCommand.
        Args:
            verify: If True, verify the VCP value after setting.
        """
        super().__init__(*args, **kwargs)

        self.verify = verify

    @classmethod
    def constructor_args_from_argparse(cls, *args, verify : bool, **kwargs) -> Dict[str, Any]:
        """
        Build constructor arguments from argparse for this command.
        Args:
            verify: If True, verify the VCP value after setting.
        Returns:
            dict: Constructor arguments.
        """
        d = super(MultiSetCliCommand, cls).constructor_args_from_argparse(*args, **kwargs)

        d['verify'] = verify

        return d


    # Execute
    def execute(self) -> None:
        """
        Execute the multi-set command: write each VCP value in sequence to the monitor.
        """
        for value in self.values:
            self.monitor.vcp_write(self.code, value, verify=self.verify)

CliCommand.CLI_COMMAND_TYPES['multi-set'] = MultiSetCliCommand
