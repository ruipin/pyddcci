# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, Dict, Any
from abc import ABCMeta

from ...ddcci.vcp.code import VcpCode

class CodeCliCommandMixin(metaclass=ABCMeta):
    """
    Mixin for CLI commands that operate on a VCP code.
    Resolves and validates the code argument for the command.
    """
    def __init__(self, code : Union[str, int], *args, **kwargs):
        try:
            self.code = self.monitor.codes[code]
        except KeyError as e:
            raise ValueError(f"Code '{code}' is not a legal code for monitor '{self.monitor.instance_name}'") from e

        super().__init__(*args, **kwargs)


    @classmethod
    def constructor_args_from_argparse(cls, code : Union[str, int], *args, **kwargs) -> Dict[str, Any]:
        d = super(CodeCliCommandMixin, cls).constructor_args_from_argparse(*args, **kwargs)

        d['code'] = code

        return d
