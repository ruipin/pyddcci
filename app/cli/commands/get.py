# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Any

from . import CliCommand, FilterCliCommandMixin, CodeCliCommandMixin

class GetCliCommand(FilterCliCommandMixin, CodeCliCommandMixin, CliCommand):
    def __init__(self, *args, raw : bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        self.raw = raw

    @classmethod
    def constructor_args_from_argparse(cls, *args, raw : bool, **kwargs) -> Dict[str, Any]:
        d = super(GetCliCommand, cls).constructor_args_from_argparse(*args, **kwargs)

        d['raw'] = raw

        return d


    # Execute
    def execute(self) -> None:
        value = self.monitor.vcp_read(self.code)

        if self.raw:
            print(value.value)
        else:
            print(value)

CliCommand.CLI_COMMAND_TYPES['get'] = GetCliCommand