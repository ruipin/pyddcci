# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import re
from typing import Any, Union, List, Optional
from abc import ABCMeta, abstractmethod

from .os import OsMonitor
from .os import OsMonitorList

from app.util import Namespace, LoggableMixin, HierarchicalMixin, NamedMixin


#############
# Base class
class BaseMonitorFilter(Namespace, LoggableMixin, HierarchicalMixin, NamedMixin, metaclass=ABCMeta):
    """
    Base class for filtering OsMonitor objects
    Implementations should define <match>, which returns True if a specific OsMonitor matches the current filter.

    These filters can then be used in the Monitor class in order to select which monitors to act on
    """

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


#############
# Regex class
class RegexMonitorFilter(BaseMonitorFilter):
    def __init__(self, filters : Union[str, re.Pattern, List[Union[str, re.Pattern]]], instance_parent=None):
        if isinstance(filters, str):
            filters = [filters]

        super().__init__(instance_name='/'.join(filters).replace(' ',''), instance_parent=instance_parent)

        for i, k in enumerate(filters):
            if not isinstance(k, re.Pattern):
                filters[i] = re.compile(k, re.I)

        if len(filters) == 0:
            raise ValueError("'filters' must not be empty")

        self.filters = filters
        self.instance_name = self.get_monitor_name()

        self.freeze_schema()

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


#############
# Regex class
class OsMonitorMonitorFilter(BaseMonitorFilter):
    def __init__(self, os_monitor : OsMonitor, instance_parent=None):
        super().__init__(instance_name=f"{os_monitor.instance_name}Filter", instance_parent=instance_parent)

        self.os_monitor = os_monitor

        self.freeze()

    def match(self, os_monitor : OsMonitor):
        return os_monitor is self.os_monitor

    # Custom implementation to avoid an expensive search when we already know which monitor we want
    def find(self, _):
        if not self.os_monitor.connected:
            return []

        return [self.os_monitor]

    # It is possible to convert this to a regex filter
    def get_regexes(self) -> List[re.Pattern]:
        m = self.os_monitor.info.monitor

        result = []

        def _add(result, to_add):
            if isinstance(to_add, str):
                result.append(re.compile(fr"^{re.escape(to_add)}$"))

        _add(result, m.model          )
        _add(result, m.serial         )
        _add(result, m.uid            )
        _add(result, m.manufacturer_id)
        _add(result, m.product_id     )

        return result

    def to_regex_filter(self) -> RegexMonitorFilter:
        return RegexMonitorFilter(self.get_regexes(), instance_parent=self.instance_parent)


    # Utilities / Logging
    def get_monitor_name(self, prefix='', suffix='') -> str:
        return f"{prefix}{self.os_monitor.instance_name}{suffix}"



# Factory
def create_monitor_filter_from(filter : Union[str, re.Pattern, List[Union[str, re.Pattern]], BaseMonitorFilter, OsMonitor], instance_parent=None):
    if isinstance(filter, BaseMonitorFilter):
        return filter

    if isinstance(filter, OsMonitor):
        return OsMonitorMonitorFilter(filter, instance_parent=instance_parent)

    return RegexMonitorFilter(filter, instance_parent=instance_parent)
