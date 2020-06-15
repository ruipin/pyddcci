# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import re

from typing import Union, List

from .base import BaseMonitorFilter
from .primary import PrimaryMonitorFilter
from .regex import RegexMonitorFilter
from .info import MonitorInfoMonitorFilter
from .os_monitor import OsMonitorMonitorFilter

from ..os import OsMonitor

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