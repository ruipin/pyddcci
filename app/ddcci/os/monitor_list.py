# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta

from . import BaseOsMonitorInfo
from . import BaseOsMonitor

from app.util import NamespaceList, LoggableHierarchicalNamedMixin, CFG



##############
# MonitorList class
class BaseOsMonitorList(NamespaceList, LoggableHierarchicalNamedMixin, metaclass=ABCMeta):
    """
    Base class for a list of OS monitors.
    Should be subclassed for OS-specific implementations. Handles enumeration and management of monitor objects.
    """

    OS_MONITOR_CLASS      = BaseOsMonitor
    OS_MONITOR_INFO_CLASS = BaseOsMonitorInfo

    def __init__(self, name=None):
        super().__init__(instance_name=name)

        self.enumerate()

        if CFG.app.cli.list_monitors:
            self.list_monitors()


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
                monitor = self.__class__.OS_MONITOR_CLASS(info, instance_parent=self)

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


    def list_monitors(self):
        import oyaml as yaml

        lst = []

        for monitor in self:
            lst.append(monitor.info.asdict(recursive=True, private=False, protected=False, public=True))

        print(yaml.dump(lst))
