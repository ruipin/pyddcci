# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Logging configuration and utilities for pyddcci.
Configures file and TTY logging, log levels, and custom handlers.
"""

import logging
import sys
import os
import atexit

from typing import override, Protocol, runtime_checkable

from . import CFG

# Log file name is hardcoded
if not isinstance(CFG.app.name, str):
    raise TypeError("CFG.app.name must be a string, got: {}".format(type(CFG.app.name)))
LOG_FILE_NAME = '{}.log'.format(CFG.app.name)

if not isinstance(CFG.logging.dir, str):
    raise TypeError("CFG.logging.dir must be a string, got: {}".format(type(CFG.logging.dir)))
LOG_FILE = os.path.join(CFG.logging.dir, LOG_FILE_NAME)

# Grab verbosity from config files
def arg_to_log_level(arg) -> int:
    """
    Convert a string or integer argument to a logging level.

    Args:
        arg (str|int): The argument to convert (e.g., 'INFO', 20, -1).
    Returns:
        int: The corresponding logging level.
    Raises:
        RuntimeError: If the argument is not a valid logging level.
    """
    # Try to convert to Integer
    try:
        arg = int(arg)
    except ValueError:
        pass

    # String, e.g. 'INFO' or 'CRITICAL'
    if isinstance(arg, str):
        level = getattr(logging, arg.upper(), None)
        if level is None:
            raise RuntimeError("Invalid logging verbosity: {}".format(arg.upper()))

    # Integer
    else:
        if arg < 0:
            level = -1
        elif arg > 50:
            level = 0
        else:
            level = 50 - int(arg)

    return level

FILE_LOGGING_LEVEL = arg_to_log_level(CFG.logging.levels.file)
TTY_LOGGING_LEVEL = min(arg_to_log_level(CFG.logging.levels.tty), logging.CRITICAL)  # Always log critical events to TTY
DEFAULT_LOGGING_LEVEL = 0  # To avoid any message being ignored even if the tty logging level changes dynamically

# Configure root logger
logging.captureWarnings(True)
logging.root.setLevel(DEFAULT_LOGGING_LEVEL)

# Create file handler
fh = None
if FILE_LOGGING_LEVEL >= 0:
    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE))
    fh = logging.FileHandler(LOG_FILE, mode='w')
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter('%(asctime)s [%(levelname)s:%(name)s] %(message)s')
    fh.setFormatter(fh_formatter)
    logging.root.addHandler(fh)

# Create tty handler
if TTY_LOGGING_LEVEL >= 0:
    ch = None

    # The unittest module mocks stderr when the test starts, so we need to dynamically use sys.stderr instead of being able to use the current sys.stderr
    if CFG.app.test:
        class UnitTestStreamHandler(logging.StreamHandler):
            @property
            @override
            def stream(self):
                return sys.stderr

            @stream.setter
            def stream(self, value):
                pass
        ch = UnitTestStreamHandler()
    else:
        ch = logging.StreamHandler(sys.stderr)

    ch.setLevel(TTY_LOGGING_LEVEL)
    ch_formatter = logging.Formatter('[%(levelname)s:%(name)s] %(message)s')
    ch.setFormatter(ch_formatter)
    logging.root.addHandler(ch)


# Also log uncaught exceptions using "logging" object, this way they also show up in the log
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_exception

# Add our custom handler to keep track of log messages
class CustomHandler(logging.Handler):
    """
    Custom logging handler to track log message counts and handle application exit status.
    """
    class ExitStatusFormatter(logging.Formatter):
        @override
        def format(self, record):
            return record.msg

    def atexit(self):
        """
        Handle application exit, print summary, and save config if appropriate.
        """
        success = True if self.num_error == 0 and self.num_critical == 0 else False

        # Make sure to save configuration when we exit, as long as we didn't fail due to a critical error (and this isn't a unit test)
        if self.num_critical == 0 and not CFG.app.test:
            print()  # Line break
            CFG.save()

        # Log success/failure
        if success:
            if self.num_warning > 0:
                exit_str = "\n****** {} terminated with {:d} warning{}! ******".format(CFG.app.name, self.num_warning, '' if self.num_warning == 1 else 's')
            else:
                exit_str = "\n{} terminated successfuly.".format(CFG.app.name)
        else:
            errors = self.num_error + self.num_critical
            exit_str = "\n****** {} terminated with {} error{}! ******" \
                       "\n  Warnings: {:6d}" \
                       "\n  Errors:   {:6d}".format(
                           CFG.app.name, 'an ' if errors == 1 else 'multiple', '' if errors == 1 else 's', self.num_warning, self.num_error + self.num_critical
                       )

        print(exit_str, file=sys.stderr)

        if fh is not None:
            if ch is not None:
                logging.root.removeHandler(ch)

            fh.setFormatter(self.ExitStatusFormatter())
            logging.log(1000, exit_str)

        # Done
        logging.shutdown()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_warning = 0
        self.num_error = 0
        self.num_critical = 0

        atexit.register(self.atexit)

    @override
    def handle(self, record) -> bool:
        if record.levelno >= logging.CRITICAL:
            self.num_critical += 1
            sys.exit(-1)
        elif record.levelno >= logging.ERROR:
            self.num_error += 1
        elif record.levelno >= logging.WARNING:
            self.num_warning += 1
        return True

customHdlr = CustomHandler()
customHdlr.setLevel(logging.INFO)
logging.root.addHandler(customHdlr)


#############
@runtime_checkable
class LoggableProtocol(Protocol):
    @property
    def log(self) -> logging.Logger: ...

# Helper for class constructors to obtain a logger object
# Returns a logger object
def getLogger(obj, parent:LoggableProtocol|None=None, name:str|None=None) -> logging.Logger:
    if name is None:
        if isinstance(obj, str):
            name = obj
        else:
            cls_name = obj.__class__.__name__
            if isinstance(cls_name, str):
                name = cls_name
            else:
                raise TypeError("Cannot determine logger name from object: {}".format(obj))

    if parent is None or not hasattr(parent, 'log'):
        return logging.getLogger(name)
    else:
        return parent.log.getChild(name)
