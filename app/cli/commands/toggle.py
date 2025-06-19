# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Any

from . import CliCommand, FilterCliCommandMixin, CodeCliCommandMixin, ValuesCliCommandMixin

class ToggleCliCommand(FilterCliCommandMixin, CodeCliCommandMixin, ValuesCliCommandMixin, CliCommand):
    """
    CLI command to toggle a VCP code between multiple values on a monitor.
    Supports optional verification after setting the value.
    """
    def __init__(self, *args, verify : bool = False, **kwargs):
        """
        Initialize the ToggleCliCommand.
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
        d = super(ToggleCliCommand, cls).constructor_args_from_argparse(*args, **kwargs)

        d['verify'] = verify

        return d


    # Execute
    def execute(self) -> None:
        """
        Execute the toggle command: cycle the VCP value on the monitor.
        """
        current = self.monitor.vcp_read(self.code)

        for i, value in enumerate(self.values):
            if value == current:
                break

        to_write = self.values[(i+1) % len(self.values)]

        self.monitor.vcp_write(self.code, to_write, verify=self.verify)

CliCommand.CLI_COMMAND_TYPES['toggle'] = ToggleCliCommand
