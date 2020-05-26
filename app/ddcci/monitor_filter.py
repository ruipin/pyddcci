# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import re
from typing import Any, Union, List, Optional
from abc import ABCMeta, abstractmethod

from .os import OsMonitor
from .os import OsMonitorList

from . import Namespace, getLogger

log = getLogger(__name__)


#############
# Base class
class BaseMonitorFilter(Namespace, metaclass=ABCMeta):
    __slots__ = Namespace.__slots__

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
            msg = '\n\t'.join([x.log_name for x in match])
            self.log.warn(f"Found more than one monitor, returning None. The following monitors matched this filter:\n\t{msg}")
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
    __slots__ = BaseMonitorFilter.__slots__

    def __init__(self, filters : Union[str, re.Pattern, List[Union[str, re.Pattern]]], parent=None):
        if isinstance(filters, str):
            filters = [filters]

        super().__init__('/'.join(filters).replace(' ',''), parent=parent)

        for i, k in enumerate(filters):
            if not isinstance(k, re.Pattern):
                filters[i] = re.compile(k, re.I)

        if len(filters) == 0:
            raise ValueError("'filters' must not be empty")

        self.filters = filters
        self.log_name = self.get_monitor_name()

    def _match_single(self, filter : re.Pattern, key : str, value : Any) -> bool:
        if value is None:
            return False

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




