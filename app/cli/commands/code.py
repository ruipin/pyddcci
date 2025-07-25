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
        """
        Initialize the mixin and resolve the VCP code.
        Args:
            code: The VCP code (alias or int).
        Raises:
            ValueError: If the code is not valid for the monitor.
        """
        try:
            self.code = self.monitor.codes[code]
        except KeyError as e:
            raise ValueError(f"Code '{code}' is not a legal code for monitor '{self.monitor.instance_name}'") from e

        super().__init__(*args, **kwargs)


    @classmethod
    def constructor_args_from_argparse(cls, code : Union[str, int], *args, **kwargs) -> Dict[str, Any]:
        """
        Build constructor arguments from argparse for this mixin.
        Args:
            code: The code string from argparse.
        Returns:
            dict: Constructor arguments.
        """
        d = super(CodeCliCommandMixin, cls).constructor_args_from_argparse(*args, **kwargs)

        d['code'] = code

        return d
