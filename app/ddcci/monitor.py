# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from .os import OsMonitorList

from . import Namespace, Sequence, getLogger
log = getLogger(__name__)


##########
# Global list of OsMonitors
OS_MONITORS = OsMonitorList()



##########
# Monitor class
class Monitor(Namespace):
    """
    Monitor class

    This is the 'user-visible' class. It represents a OsMonitor, given a filter.
    When it needs to operate on the OsMonitor, it will dynamically search for the OsMonitor that matches the filter.

    This allows us to configure/remember monitors independently from whether they are connected.
    It also allows us to be flexible if the monitor information changes.
    """

    __slots__ = Namespace.__slots__