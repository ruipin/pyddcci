# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Any

from . import CliCommand, FilterCliCommandMixin, CodeCliCommandMixin, ValueCliCommandMixin

class SetCliCommand(FilterCliCommandMixin, CodeCliCommandMixin, ValueCliCommandMixin, CliCommand):
    """
    CLI command to set a VCP code value on a monitor.
    Supports optional verification after setting the value.
    """
    def __init__(self, *args, verify : bool = False, **kwargs):
        """
        Initialize the SetCliCommand.
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
        d = super(SetCliCommand, cls).constructor_args_from_argparse(*args, **kwargs)

        d['verify'] = verify

        return d


    # Execute
    def execute(self) -> None:
        """
        Execute the set command: write the VCP value to the monitor.
        """
        self.monitor.vcp_write(self.code, self.value, verify=self.verify)

CliCommand.CLI_COMMAND_TYPES['set'] = SetCliCommand