# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta

from . import BaseOsMonitorInfo
from . import BaseOsMonitor

from . import getLogger, Sequence
log = getLogger(__name__)



##############
# MonitorList class
class BaseOsMonitorList(Sequence, metaclass=ABCMeta):
    """
    List of OS Monitors
    This is a base class, and should be inherited by a OS-specific class
    """

    OS_MONITOR_CLASS      = BaseOsMonitor
    OS_MONITOR_INFO_CLASS = BaseOsMonitorInfo

    def __init__(self, name=None):
        super().__init__(log_name=name)

        self.enumerate()


    def enumerate(self):
        # Obtain list of current monitor information
        infos = self.__class__.OS_MONITOR_INFO_CLASS.enumerate()

        # Match with existing monitors
        new_monitors = set()

        for info in infos:
            # Find a matching monitor
            for monitor in self:
                if monitor.info.represents_same_monitor(info):
                    monitor.info.update(info)
                    break

            else:
                # No matching monitor found. Create new monitor
                monitor = self.__class__.OS_MONITOR_CLASS(info, parent=self)

            new_monitors.add(monitor)

        assert(len(new_monitors) == len(infos))

        # Replace existing array with new one
        old_monitors = self._list
        self.replace(list(new_monitors))

        # Notify any monitor that got disconnected
        for monitor in old_monitors:
            if monitor not in new_monitors:
                monitor.on_disconnect()

        # Notify any monitor that just got connected
        for monitor in self:
            if not monitor.connected:
                monitor.on_connect()
