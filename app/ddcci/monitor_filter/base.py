# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import List, Optional, Dict
from abc import ABCMeta, abstractmethod

from ..os import OsMonitor, OsMonitorList

from app.util import NamespaceMap, LoggableMixin, HierarchicalMixin, NamedMixin


#############
# Base class
class BaseMonitorFilter(NamespaceMap, LoggableMixin, HierarchicalMixin, NamedMixin, metaclass=ABCMeta):
    """
    Abstract base class for filtering OsMonitor objects.

    Subclasses implement match() to select monitors based on criteria. Used for monitor selection in pyddcci.
    Provides serialization, naming, and logging support.
    """
    FILTER_TYPES = {}


    # Filtering
    @abstractmethod
    def match(self, os_monitor : OsMonitor) -> bool:
        pass

    def find(self, os_monitor_list : OsMonitorList) -> List[OsMonitor]:
        match = []

        for os_monitor in os_monitor_list:
            if self.match(os_monitor):
                match.append(os_monitor)

        return match

    def find_one(self, os_monitor_list : OsMonitorList) -> Optional[OsMonitor]:
        match = self.find(os_monitor_list)
        len_match = len(match)

        if len_match > 1:
            msg = '\n\t'.join([x.instance_name for x in match])
            self.log.warning(f"Found more than one monitor, returning None. The following monitors matched this filter:\n\t{msg}")
            return None

        if len_match == 0:
            return None

        return match[0]


    # Naming
    @abstractmethod
    def get_monitor_name(self, prefix='<', suffix='>') -> str:
        pass


    # Serialization
    def serialize(self) -> Dict:
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, data : Dict, instance_parent=None) -> 'BaseMonitorFilter':
        if 'type' not in data:
            raise ValueError(f"'data' dictionary must contain key 'type'")

        data = dict(data)
        typ = data.pop('type')

        _cls = cls.FILTER_TYPES.get(typ, None)
        if _cls is None:
            raise ValueError(f"Invalid filter type {typ}")

        return _cls.deserialize(data, instance_parent=instance_parent)