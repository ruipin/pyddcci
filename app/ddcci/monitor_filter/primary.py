# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict
from collections import OrderedDict

from . import BaseMonitorFilter
from ..os import OsMonitor


class PrimaryMonitorFilter(BaseMonitorFilter):
    """
    Monitor filter that matches the primary monitor (as reported by the OS).
    Used for selecting the main display in multi-monitor setups.
    """
    def __init__(self, instance_parent=None):
        super().__init__(instance_parent=instance_parent)

        self.instance_name = self.get_monitor_name()
        self.freeze_map()

    def match(self, os_monitor : OsMonitor) -> bool:
        return os_monitor.info.adapter.primary


    # Utilities / Logging
    def get_monitor_name(self, prefix='', suffix='') -> str:
        return f'{prefix}Primary{suffix}'


    # Equality
    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __hash__(self):
        return hash(self.__class__)


    # Serialization
    def serialize(self) -> Dict:
        return OrderedDict(type='primary')

    @classmethod
    def deserialize(cls, data : Dict, instance_parent=None) -> 'PrimaryMonitorFilter':
        if 'type' in data:
            typ = data.pop('type')
            assert typ == 'primary'

        return cls(instance_parent=instance_parent)


BaseMonitorFilter.FILTER_TYPES['primary'] = PrimaryMonitorFilter
