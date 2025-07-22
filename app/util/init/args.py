# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Argument parsing and CLI option definitions for pyddcci.
Defines global options, command actions, and wraps argparse for use throughout the application.
"""

import sys
import argparse
import os
import re
from typing import override

###################
# Script name corresponds to argv[0] (without the '.py' extension, if present)
if len(sys.argv) > 0 and sys.argv[0]:
    EXE_NAME = os.path.basename(sys.argv[0])
    NAME = re.sub("\\.py$", '', EXE_NAME, flags=re.I)
else:
    NAME = 'pyddcci'


###################
# Script home
HOME = os.path.realpath(os.path.join(__file__, '../../../..'))


###################
# Unit test
def is_unit_test() -> bool:
    """
    Test whether running in a unit test environment.

    Returns:
        bool: True if running in a unit test environment, False otherwise.
    """
    env = os.environ.get("UNIT_TEST", None)
    if env is not None:
        env = env.strip()
    if not env:
        return False

    if env.lower() in ('false', '0', 'no'):
        return False

    return True

UNIT_TEST = is_unit_test()


###################
# Argument parser
_PARSER = argparse.ArgumentParser()

def add_arg(name, *args, default=None, **kwargs):
    """
    Add a command-line argument to the global parser.

    Args:
        name (str): The destination variable name.
        *args: Argument flags (e.g., '-v', '--verbosity').
        default: Default value if not set elsewhere.
        **kwargs: Additional argparse options.
    """
    _PARSER.add_argument(*args,
        dest=name,
        default=os.getenv("PYDDCCI_{}".format(name.upper()).replace('.','_'), default),
        **kwargs
    )


# Argument definitions
add_arg('logging.levels.file', '-lv', '--log-verbosity', action='store', help='Logfile verbosity. Can be numeric or one of the default logging levels (CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10)')
add_arg('logging.levels.tty' , '-v', '--verbosity', action='store', help='Console verbosity. Can be numeric or one of the default logging levels (CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10)')

add_arg('app.cli.list_monitors', '-l', '--list', '--list-monitors', action='store_const', const=True, default=False)


# CLI commands
class CommandAction(argparse.Action):
    """
    Custom argparse action for handling CLI command arguments (get, set, multi-set, toggle).
    Parses and validates command arguments and stores them in the namespace.
    """
    GET_PARSER = argparse.ArgumentParser(prefix_chars='+')
    GET_PARSER.add_argument('+r', '+raw', dest='raw', action='store_const', const=True, default=False)

    SET_PARSER = argparse.ArgumentParser(prefix_chars='+')
    SET_PARSER.add_argument('+v', '+verify', dest='verify', action='store_const', const=True, default=True)
    SET_PARSER.add_argument('+nv', '+no_verify', dest='verify', action='store_const', const=False)

    TOGGLE_PARSER = SET_PARSER

    @override
    def __call__(self, parser, namespace, values, option_string=None):
        """
        Parse and validate CLI command arguments, storing them in the namespace.

        Args:
            parser: The argparse parser instance.
            namespace: The argparse namespace.
            values: The argument values.
            option_string: The option string used (e.g., '-g', '-s').

        Raises:
            ValueError: If the command arguments are invalid.
        """
        if option_string in ('-s', '--set'):
            typ = 'set'
            args, unknown = self.__class__.SET_PARSER.parse_known_args(values)

            if len(unknown) != 3:
                raise ValueError(f"Illegal 'set' command: {values}")

        elif option_string in ('-ms', '--multi-set'):
            typ = 'multi-set'
            args, unknown = self.__class__.SET_PARSER.parse_known_args(values)

            if len(unknown) < 3:
                raise ValueError(f"Illegal 'multi-set' command: {values}")

        elif option_string in ('-g', '--get'):
            typ = 'get'
            args, unknown = self.__class__.GET_PARSER.parse_known_args(values)

            if len(unknown) != 2:
                raise ValueError(f"Illegal 'set' command: {values}")

        elif option_string in ('-t', '--toggle'):
            typ = 'toggle'
            args, unknown = self.__class__.TOGGLE_PARSER.parse_known_args(values)

            if len(unknown) < 3:
                raise ValueError(f"Illegal 'toggle' command: {values}")

        else:
            raise ValueError(f"Invalid option_string={option_string}")

        if not hasattr(namespace, self.dest) or getattr(namespace, self.dest) is None:
            setattr(namespace, self.dest, [])

        getattr(namespace, self.dest).append({
            'type'  : typ,
            'args'  : vars(args),
            'others': unknown
        })

_PARSER.add_argument('-s' , '--set'      , dest='app.cli.commands', nargs='+', action=CommandAction)
_PARSER.add_argument('-ms', '--multi-set', dest='app.cli.commands', nargs='+', action=CommandAction)
_PARSER.add_argument('-g' , '--get'      , dest='app.cli.commands', nargs='+', action=CommandAction)
_PARSER.add_argument('-t' , '--toggle'   , dest='app.cli.commands', nargs='+', action=CommandAction)
_PARSER.add_argument('-ie', '--ignore-errors', dest='app.cli.ignore_errors', action='store_const', const=True, default=False)


###################
# End of argument definitions
ARGS = _PARSER.parse_args(sys.argv[1:] if not UNIT_TEST else '')

if getattr(ARGS, 'app.cli.commands', None) is None:
    setattr(ARGS, 'app.cli.commands', [])



###################
# Wrap 'ARGS' accesses
def __getattr__(name):
    """
    Get an attribute using attribute syntax obj.name.

    Args:
        name: The attribute name.

    Returns:
        The attribute value.
    """
    return getattr(ARGS, name)

def __getitem__(key):
    """
    Get an attribute using dictionary syntax obj[key].

    Args:
        key: The attribute name.

    Returns:
        The attribute value.
    """
    return getattr(ARGS, key)