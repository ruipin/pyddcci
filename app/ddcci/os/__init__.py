# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from .. import Namespace, Sequence, getLogger

# Import base classes first
from .monitor_info   import BaseOsMonitorInfo
from .monitor        import BaseOsMonitor
from .monitor_list   import BaseOsMonitorList
from .vcp_code       import BaseOsVcpCode

# Now import OS-specific specializations
from .windows.monitor_info import WindowsOsMonitorInfo as OsMonitorInfo
from .windows.monitor      import WindowsOsMonitor     as OsMonitor
from .windows.monitor_list import WindowsOsMonitorList as OsMonitorList
from .windows.vcp_code     import WindowsOsVcpCode     as OsVcpCode