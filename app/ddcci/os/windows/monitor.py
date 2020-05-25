# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from ..monitor import BaseOsMonitor

from . import getLogger
log = getLogger(__name__)



##########
# OS Monitor class
class WindowsOsMonitor(BaseOsMonitor):
    """
    Windows implementation of BaseOsMonitor
    """

    __slots__ = BaseOsMonitor.__slots__
