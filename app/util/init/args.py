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
        default=os.getenv("PYDDCCI_{}".format(name.upper()), default),
        **kwargs
    )


# Argument definitions
add_arg('logging.level.file', '-lv', '--log-verbosity', help='Logfile verbosity. Can be numeric or one of the default logging levels (CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10)')
add_arg('logging.level.tty' , '-v', '--verbosity', help='Console verbosity. Can be numeric or one of the default logging levels (CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10)')


###################
# End of argument definitions
ARGS = _PARSER.parse_args()


###################
# Wrap 'ARGS' accesses
def __getattr__(name):
    """ Get an attribute using attribute syntax obj.name """
    return getattr(ARGS, name)

def __getitem__(key):
    """ Get an attribute using dictionary syntax obj[key] """
    return getattr(ARGS, key)