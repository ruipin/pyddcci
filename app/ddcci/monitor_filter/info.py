# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict
from collections import OrderedDict

from . import BaseMonitorFilter

from ..os import OsMonitor

class MonitorInfoMonitorFilter(BaseMonitorFilter):
    def __init__(self, model, serial, uid, manufacturer_id, product_id, instance_parent=None):
        super().__init__(instance_parent=instance_parent)

        self.model           = model
        self.serial          = serial
        self.uid             = uid
        self.manufacturer_id = manufacturer_id
        self.product_id      = product_id

        self.instance_name = self.get_monitor_name()
        self.freeze_map()

    def match(self, os_monitor : OsMonitor):
        m = os_monitor.info.monitor

        for attr, v in self.items():
            if v != getattr(m, attr):
                return False

        return True


    # Equality
    def __eq__(self, other):
        from . import OsMonitorMonitorFilter
        if isinstance(other, OsMonitorMonitorFilter):
            return self == other.to_monitor_info_filter()

        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __hash__(self):
        return super().__hash__()


    # Utilities / Logging
    def get_monitor_name(self, prefix='', suffix='') -> str:
        return f"{prefix}{self.model}/{self.serial}/{self.uid}/{self.manufacturer_id}/{self.product_id}{suffix}"


    # Serialization
    def serialize(self) -> Dict:
        d = OrderedDict(type='info')
        d.update(self.asdict(private=False, protected=False, public=True))
        return d

    @classmethod
    def deserialize(cls, data : Dict, instance_parent=None) -> 'MonitorInfoMonitorFilter':
        if 'type' in data:
            typ = data.pop('type')
            assert typ == 'info'
        return cls(**data)


BaseMonitorFilter.FILTER_TYPES['info'] = MonitorInfoMonitorFilter
