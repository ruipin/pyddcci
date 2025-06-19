# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, Dict, Any, List
from abc import ABCMeta


class ValueCliCommandMixin(metaclass=ABCMeta):
    """
    Mixin for CLI commands that operate on a single VCP value.
    Resolves and validates the value argument for the command.
    """
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


class ValuesCliCommandMixin(metaclass=ABCMeta):
    """
    Mixin for CLI commands that operate on multiple VCP values.
    Resolves and validates the values argument for the command.
    """
    def __init__(self, values : List[Union[str, int]], **kwargs):
        self.values = []
        for value in values:
            try:
                    self.values.append(self.code[value])
            except KeyError as e:
                raise ValueError(f"Value '{value}' is not a legal value for code '{self.code}' (0x{self.code.code:X})") from e

        super().__init__(**kwargs)


    @classmethod
    def constructor_args_from_argparse(cls, *values : List[Union[str, int]], **kwargs) -> Dict[str, Any]:
        d = super(ValuesCliCommandMixin, cls).constructor_args_from_argparse(**kwargs)

        if len(values) == 0:
            raise ValueError("No values provided")

        d['values'] = values

        return d
