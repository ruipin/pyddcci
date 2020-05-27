# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Callable, Optional, Iterable, Mapping


class EnterExitCall(object):
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
        args   = self.args_enter   or ()
        kwargs = self.kwargs_enter or {}
        self.mthd_enter(*args, **kwargs)

    def __enter__(self):
        self.enter()

    def exit(self):
        args   = self.args_exit   or ()
        kwargs = self.kwargs_exit or {}
        self.mthd_exit(*args, **kwargs)

    def __exit__(self, _, __, ___):
        self.exit()