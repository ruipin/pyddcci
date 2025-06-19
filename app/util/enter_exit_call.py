# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Callable, Optional, Iterable, Mapping


class EnterExitCall(object):
    """
    Context manager to call enter and exit methods with optional arguments.
    Useful for temporarily changing state (e.g., freezing/unfreezing) in a with-block.

    Args:
        mthd_enter: Callable to invoke on enter.
        mthd_exit: Callable to invoke on exit.
        args_enter: Positional arguments for enter.
        kwargs_enter: Keyword arguments for enter.
        args_exit: Positional arguments for exit.
        kwargs_exit: Keyword arguments for exit.
    """
    def __init__(self, mthd_enter : Callable, mthd_exit : Callable,
                 args_enter: Optional[Iterable] = None, kwargs_enter: Optional[Mapping] = None,
                 args_exit : Optional[Iterable] = None, kwargs_exit : Optional[Mapping] = None):

        self.mthd_enter   = mthd_enter
        self.args_enter   = args_enter
        self.kwargs_enter = kwargs_enter

        self.mthd_exit   = mthd_exit
        self.args_exit   = args_exit
        self.kwargs_exit = kwargs_exit

        self.enter()

    def enter(self):
        """
        Call the enter method with provided arguments.
        """
        args   = self.args_enter   or ()
        kwargs = self.kwargs_enter or {}
        self.mthd_enter(*args, **kwargs)

    def __enter__(self):
        """
        Enter the context (calls enter method).
        """
        self.enter()

    def exit(self):
        """
        Call the exit method with provided arguments.
        """
        args   = self.args_exit   or ()
        kwargs = self.kwargs_exit or {}
        self.mthd_exit(*args, **kwargs)

    def __exit__(self, _, __, ___):
        """
        Exit the context (calls exit method).
        """
        self.exit()