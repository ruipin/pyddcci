# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Any
from abc import ABCMeta, abstractmethod

from app.util import NamespaceMap, LoggableMixin

class CliCommand(LoggableMixin, metaclass=ABCMeta):
    CLI_COMMAND_TYPES = {}

    @classmethod
    def constructor_args_from_argparse(cls) -> Dict[str, Any]:
        return {}

    @classmethod
    def from_argparse(cls, command : Dict) -> 'CliCommand':
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


    # Execute
    @abstractmethod
    def execute(self) -> None:
        pass


"""
for i, command in enumerate(commands):
    try:
        cmd = command[0]
        args = command[1:]

        # Set VCP code
        if cmd == 'set':
            if len(args) != 3:
                raise RuntimeError("'set' commands require 3 arguments: filter, code, value")

            filter = args[0]
            code = args[1]
            value = args[2]

            from app.ddcci.monitor import Monitor

            monitor = Monitor(filter)
            monitor.vcp_write(code, value)

        # Get VCP code
        elif cmd == 'get':
            if len(args) != 2:
                raise RuntimeError("'get' commands require 2 arguments: filter, code")

            filter = args[0]
            code = args[1]

            from app.ddcci.monitor import Monitor

            monitor = Monitor(filter)
            print(monitor.vcp_read(code))

        # Error
        else:
            raise ValueError(f"Invalid command '{cmd}'")

    except Exception as e:
        if not CFG.app.cli.ignore_errors:
            raise RuntimeError(f"Failed to execute command #{i}: {command}") from e
"""