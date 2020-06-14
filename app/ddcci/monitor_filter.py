# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import re
from typing import Any, Union, List, Optional, Dict
from collections import OrderedDict
from abc import ABCMeta, abstractmethod

from .os import OsMonitor, OsMonitorList

from app.util import NamespaceMap, LoggableMixin, HierarchicalMixin, NamedMixin


#############
# Base class
class BaseMonitorFilter(NamespaceMap, LoggableMixin, HierarchicalMixin, NamedMixin, metaclass=ABCMeta):
    """
    Base class for filtering OsMonitor objects
    Implementations should define <match>, which returns True if a specific OsMonitor matches the current filter.

    These filters can then be used in the Monitor class in order to select which monitors to act on
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



#############
# Implementations
class PrimaryMonitorFilter(BaseMonitorFilter):
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


class RegexMonitorFilter(BaseMonitorFilter):
    def __init__(self, filters : Union[str, re.Pattern, List[Union[str, re.Pattern]]], instance_parent=None):
        if isinstance(filters, str):
            filters = [filters]

        super().__init__(instance_parent=instance_parent)

        for i, k in enumerate(filters):
            if not isinstance(k, re.Pattern):
                filters[i] = re.compile(k, re.I)

        if len(filters) == 0:
            raise ValueError("'filters' must not be empty")

        self.filters = filters

        self.instance_name = self.get_monitor_name()
        self.freeze_map()

    def _match_single(self, filter : re.Pattern, key : str, value : Any) -> bool:
        if value is None:
            return False

        if callable(getattr(value, 'items', None)):
            for sub_key, sub_value in value.items():
                if self._match_single(filter, sub_key, sub_value):
                    return True

        if callable(getattr(value, 'items', None)):
            for sub_key, sub_value in value.items():
                if self._match_single(filter, sub_key, sub_value):
                    return True

            return False

        if key == 'primary':
            return value and filter.search(str(key))

        return filter.search(str(value)) is not None

    def match(self, os_monitor : OsMonitor) -> bool:
        info = os_monitor.info

        # Iterate through the monitor information to see if we find a match
        for filter in self.filters:
            if not self._match_single(filter, 'info', info):
                return False

        return True


    # Utilities / Logging
    def get_monitor_name(self, prefix='', suffix='') -> str:
        if len(self.filters) == 1:
            return f"{prefix}{str(self.filters[0].pattern)}{suffix}"
        else:
            return f"{prefix}{{<{'> && <'.join([str(x.pattern) for x in self.filters])}>}}{suffix}"


    # Serialization
    def serialize(self) -> Dict:
        d = OrderedDict(typ='regex')

        regexes = []
        for regex in self.filters:
            regexes.append(str(regex))

        d['regexes'] = regexes

        return d

    def deserialize(self, data : Dict, instance_parent=None) -> 'RegexMonitorFilter':
        if 'type' in data:
            typ = data.pop('type')
            assert typ == 'regex'

        regexes = data.pop('regexes')
        if len(data) > 0:
            raise ValueError(f"Invalid 'regex' filter keys: {data}")

        return RegexMonitorFilter(regexes, instance_parent=instance_parent)
BaseMonitorFilter.FILTER_TYPES['regex'] = RegexMonitorFilter



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



class OsMonitorMonitorFilter(BaseMonitorFilter):
    def __init__(self, os_monitor : OsMonitor, instance_parent=None):
        super().__init__(instance_parent=instance_parent)

        self.os_monitor = os_monitor

        self.instance_name = self.get_monitor_name()
        self.freeze_map()

    def match(self, os_monitor : OsMonitor) -> bool:
        return os_monitor is self.os_monitor

    # Custom implementation to avoid an expensive search when we already know which monitor we want
    def find(self, _) -> List[OsMonitor]:
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



# Factory
def create_monitor_filter_from(filter : Union[str, re.Pattern, List[Union[str, re.Pattern]], BaseMonitorFilter, OsMonitor], instance_parent=None):
    if isinstance(filter, BaseMonitorFilter):
        assert instance_parent is None or filter.instance_parent == instance_parent
        return filter

    if isinstance(filter, OsMonitor):
        return OsMonitorMonitorFilter(filter, instance_parent=instance_parent)

    if isinstance(filter, str) and filter.strip().lower() == 'primary':
        return PrimaryMonitorFilter(instance_parent=instance_parent)

    return RegexMonitorFilter(filter, instance_parent=instance_parent)
