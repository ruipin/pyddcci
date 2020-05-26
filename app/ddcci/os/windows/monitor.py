# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from .api.physical_monitor import OsMonitorPhysicalHandle
from ..monitor import BaseOsMonitor

from . import getLogger
log = getLogger(__name__)



##########
# OS Monitor class
class WindowsOsMonitor(BaseOsMonitor):
    """
    Windows implementation of BaseOsMonitor
    """

    __slots__ = BaseOsMonitor.__slots__


    # Physical Monitor
    def get_physical_handle(self) -> OsMonitorPhysicalHandle:
        return OsMonitorPhysicalHandle(self)

    def _get_capabilities_string(self) -> str:
        with self.get_physical_handle() as physical:
            return physical.get_capabilities_string()