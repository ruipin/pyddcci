# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import re

from typing import List, Union, Any, Dict
from collections import OrderedDict

from . import BaseMonitorFilter
from ..os import OsMonitor


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
