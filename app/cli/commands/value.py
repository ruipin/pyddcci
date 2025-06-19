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
        """
        Initialize the mixin and resolve the VCP value.
        Args:
            value: The VCP value (alias or int).
        Raises:
            ValueError: If the value is not valid for the code.
        """
        try:
            self.value = self.code[value]
        except KeyError as e:
            raise ValueError(f"Value '{value}' is not a legal value for code '{self.code}' (0x{self.code.code:X})") from e

        super().__init__(*args, **kwargs)


    @classmethod
    def constructor_args_from_argparse(cls, value : Union[str, int], *args, **kwargs) -> Dict[str, Any]:
        """
        Build constructor arguments from argparse for this mixin.
        Args:
            value: The value string from argparse.
        Returns:
            dict: Constructor arguments.
        """
        d = super(ValueCliCommandMixin, cls).constructor_args_from_argparse(*args, **kwargs)

        d['value'] = value

        return d


class ValuesCliCommandMixin(metaclass=ABCMeta):
    """
    Mixin for CLI commands that operate on multiple VCP values.
    Resolves and validates the values argument for the command.
    """
    def __init__(self, values : List[Union[str, int]], **kwargs):
        """
        Initialize the mixin and resolve the VCP values.
        Args:
            values: List of VCP values (aliases or ints).
        Raises:
            ValueError: If any value is not valid for the code.
        """
        self.values = []
        for value in values:
            try:
                    self.values.append(self.code[value])
            except KeyError as e:
                raise ValueError(f"Value '{value}' is not a legal value for code '{self.code}' (0x{self.code.code:X})") from e

        super().__init__(**kwargs)


    @classmethod
    def constructor_args_from_argparse(cls, *values : List[Union[str, int]], **kwargs) -> Dict[str, Any]:
        """
        Build constructor arguments from argparse for this mixin.
        Args:
            values: The value strings from argparse.
        Returns:
            dict: Constructor arguments.
        Raises:
            ValueError: If no values are provided.
        """
        d = super(ValuesCliCommandMixin, cls).constructor_args_from_argparse(**kwargs)

        if len(values) == 0:
            raise ValueError("No values provided")

        d['values'] = values

        return d
