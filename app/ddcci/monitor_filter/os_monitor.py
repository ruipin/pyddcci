# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import List, Dict

from . import BaseMonitorFilter
from . import MonitorInfoMonitorFilter

from ..os import OsMonitor


class OsMonitorMonitorFilter(BaseMonitorFilter):
    """
    Monitor filter that matches a specific OsMonitor instance.
    Used for direct selection of a known monitor object.
    """
    def __init__(self, os_monitor : OsMonitor, instance_parent=None):
        super().__init__(instance_parent=instance_parent)

        self.os_monitor = os_monitor

        self.instance_name = self.get_monitor_name()
        self.freeze_map()

    def match(self, os_monitor : OsMonitor) -> bool:
        return os_monitor is self.os_monitor

    # Custom implementation to avoid an expensive search when we already know which monitor we want
    def find(self, os_monitor_list) -> List[OsMonitor]:
        if not self.os_monitor.connected:
            return []

        return [self.os_monitor]

    # It is possible to convert this to a regex filter
    def to_monitor_info_filter(self) -> MonitorInfoMonitorFilter:
        m = self.os_monitor.info.monitor

        return MonitorInfoMonitorFilter(m.model, m.serial, m.uid, m.manufacturer_id, m.product_id, instance_parent=self.instance_parent)


    # Utilities / Logging
    def get_monitor_name(self, prefix='', suffix='') -> str:
        return f"{prefix}{self.os_monitor.instance_name}{suffix}"


    # Equality
    def __eq__(self, other):
        if isinstance(other, MonitorInfoMonitorFilter):
            return self.to_monitor_info_filter() == other

        return isinstance(other, self.__class__) and self.os_monitor == other.os_monitor

    def __hash__(self):
        return hash(self.os_monitor)


    # Serialization
    def serialize(self) -> Dict:
        return self.to_monitor_info_filter().serialize()

    def deserialize(self, data : Dict, instance_parent=None) -> 'MonitorInfoMonitorFilter':
        return MonitorInfoMonitorFilter.deserialize(data, instance_parent=instance_parent)