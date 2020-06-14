# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

# Import base classes first
from .monitor_info   import BaseOsMonitorInfo
from .monitor        import BaseOsMonitor
from .monitor_list   import BaseOsMonitorList

# Now import OS-specific specializations
from .windows.monitor_info import WindowsOsMonitorInfo as OsMonitorInfo
from .windows.monitor      import WindowsOsMonitor     as OsMonitor
from .windows.monitor_list import WindowsOsMonitorList as OsMonitorList


# Global list of OsMonitors
OS_MONITORS = OsMonitorList('Monitors')