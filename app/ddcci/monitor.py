# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import re
from typing import Union, List

from .os import OsMonitorList, VcpReply
from .monitor_filter import BaseMonitorFilter, RegexMonitorFilter

from . import Namespace, Sequence, getLogger
log = getLogger(__name__)


##########
# Global list of OsMonitors
OS_MONITORS = OsMonitorList('Monitors')



##########
# Monitor class
class Monitor(Namespace):
    """
    Monitor class

    This is the 'user-visible' class. It represents a OsMonitor, given a filter.
    When it needs to operate on the OsMonitor, it will dynamically search for the OsMonitor that matches the filter.

    This allows us to configure/remember monitors independently from whether they are connected.
    It also allows us to be flexible if the monitor information changes.
    """

    __slots__ = Namespace.__slots__

    def __init__(self, filter : Union[str, re.Pattern, List[Union[str, re.Pattern]], BaseMonitorFilter], parent=None):
        if not isinstance(filter, BaseMonitorFilter):
            filter = RegexMonitorFilter(filter)

        super().__init__(filter.get_monitor_name(prefix='', suffix=''), parent=parent)

        self.filter = filter


    # Os Monitor
    def get_os_monitor(self, enumerate=True):
        if enumerate:
            OS_MONITORS.enumerate()
        return self.filter.find_one(OS_MONITORS)


    # Raw VCP access
    def vcp_query_raw(self, code : int) -> VcpReply:
        return self.get_os_monitor().vcp_query(code)

    def vcp_read_raw(self, code : int) -> int:
        return self.get_os_monitor().vcp_read(code)

    def vcp_write_raw(self, code : int, value : int) -> None:
        return self.get_os_monitor().vcp_write(code, value)
