# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import sys
import argparse
import os
import re

###################
# Script name corresponds to argv[0] (without the '.py' extension, if present)
if len(sys.argv) > 0 and sys.argv[0]:
    EXE_NAME = os.path.basename(sys.argv[0])
    NAME = re.sub('\.py$', '', EXE_NAME, flags=re.I)
else:
    NAME = 'pyddcci'


###################
# Script home
HOME = os.path.realpath(os.path.join(__file__, '../../../..'))


###################
# Unit test
def is_unit_test():
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
    Examples:
    >>> add_arg('BASIC'  , '-b', '--basic', help='Does XYZ')
    >>> add_arg('STORE_TRUE'    , '-st', '--store-true', action='store_true', default=False, help="Defaults to False. Becomes True if arg supplied")
    >>> add_arg('APPEND', '-a', '--append', action='append', default=None, help="Append to array")
    """

    _PARSER.add_argument(*args,
        dest=name,
        default=os.getenv("PYDDCCI_{}".format(name.upper()).replace('.','_'), default),
        **kwargs
    )


# Argument definitions
add_arg('logging.levels.file', '-lv', '--log-verbosity', action='store', help='Logfile verbosity. Can be numeric or one of the default logging levels (CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10)')
add_arg('logging.levels.tty' , '-v', '--verbosity', action='store', help='Console verbosity. Can be numeric or one of the default logging levels (CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10)')


# CLI commands
class CommandAction(argparse.Action):
    GET_PARSER = argparse.ArgumentParser(prefix_chars='+')
    GET_PARSER.add_argument('+r', '+raw', dest='raw', action='store_const', const=True, default=False)

    SET_PARSER = argparse.ArgumentParser(prefix_chars='+')
    SET_PARSER.add_argument('+v', '+verify', dest='verify', action='store_const', const=True, default=True)
    SET_PARSER.add_argument('+nv', '+no_verify', dest='verify', action='store_const', const=False)

    TOGGLE_PARSER = SET_PARSER

    def __call__(self, parser, namespace, values, option_string=None):
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
ARGS = _PARSER.parse_args()

if getattr(ARGS, 'app.cli.commands', None) is None:
    setattr(ARGS, 'app.cli.commands', [])



###################
# Wrap 'ARGS' accesses
def __getattr__(name):
    """ Get an attribute using attribute syntax obj.name """
    return getattr(ARGS, name)

def __getitem__(key):
    """ Get an attribute using dictionary syntax obj[key] """
    return getattr(ARGS, key)