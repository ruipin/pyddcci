# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from .monitor_info import WindowsOsMonitorInfo
from .monitor import WindowsOsMonitor

from ..monitor_list import BaseOsMonitorList


##########
# OS Monitor class
class WindowsOsMonitorList(BaseOsMonitorList):
    """
    Windows-specific implementation of BaseOsMonitorList.
    Manages enumeration and access to Windows OS monitors.
    """

    OS_MONITOR_INFO_CLASS = WindowsOsMonitorInfo
    OS_MONITOR_CLASS      = WindowsOsMonitor
