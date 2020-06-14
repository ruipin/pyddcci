# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, Dict, Any
from abc import ABCMeta

from ...ddcci.vcp.code import VcpCode

class ValueCliCommandMixin(metaclass=ABCMeta):
    def __init__(self, value : Union[str, int], *args, **kwargs):
        try:
            self.value = self.code[value]
        except KeyError as e:
            raise ValueError(f"Value '{value}' is not a legal value for code '{self.code}' (0x{self.code.code:X})") from e

        super().__init__(*args, **kwargs)


    @classmethod
    def constructor_args_from_argparse(cls, value : Union[str, int], *args, **kwargs) -> Dict[str, Any]:
        d = super(ValueCliCommandMixin, cls).constructor_args_from_argparse(*args, **kwargs)

        d['value'] = value

        return d
