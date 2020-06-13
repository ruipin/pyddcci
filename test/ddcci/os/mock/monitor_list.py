# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from .monitor_info import MockOsMonitorInfo
from .monitor import MockOsMonitor

from app.ddcci.os.monitor_list import BaseOsMonitorList


##########
# OS Monitor class
class MockOsMonitorList(BaseOsMonitorList):
    """
    Windows implementation of BaseOsMonitorList
    """

    OS_MONITOR_INFO_CLASS = MockOsMonitorInfo
    OS_MONITOR_CLASS      = MockOsMonitor


WindowsOsMonitorList = MockOsMonitorList
