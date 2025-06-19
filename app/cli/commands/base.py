# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Base class for CLI commands and command factory logic.
Defines the interface for CLI commands and provides factory methods for instantiation from argparse.
"""

from typing import Dict, Any
from abc import ABCMeta, abstractmethod

from app.util import NamespaceMap, LoggableMixin

class CliCommand(LoggableMixin, metaclass=ABCMeta):
    """
    Abstract base class for CLI commands.
    Provides factory methods and interface for execution, to be implemented by command subclasses.
    """
    CLI_COMMAND_TYPES = {}

    @classmethod
    def constructor_args_from_argparse(cls) -> Dict[str, Any]:
        """
        Return a dictionary of constructor arguments from argparse (override in subclasses).

        Returns:
            dict: Constructor arguments for the command.
        """
        return {}

    @classmethod
    def from_argparse(cls, command : Dict) -> 'CliCommand':
        """
        Factory method to instantiate a CLI command from an argparse-parsed command dict.

        Args:
            command: Dictionary from argparse containing command info.

        Returns:
            CliCommand: The instantiated command object.

        Raises:
            ValueError: If the command dict is missing required keys or type is invalid.
        """
        if 'type' not in command:
            raise ValueError("'command' dictionary must contain key 'type'")
        if 'others' not in command:
            raise ValueError("'command' dictionary must contain key 'others'")
        if 'args' not in command:
            raise ValueError("'command' dictionary must contain key 'args'")

        command = dict(command)
        typ = command.pop('type')

        _cls = cls.CLI_COMMAND_TYPES.get(typ, None)
        if _cls is None:
            raise ValueError(f"Invalid command type '{typ}'")

        construct_args = _cls.constructor_args_from_argparse(*command['others'], **command['args'])
        return _cls(**construct_args)

    @abstractmethod
    def execute(self) -> None:
        """
        Execute the CLI command. Must be implemented by subclasses.
        """
        pass