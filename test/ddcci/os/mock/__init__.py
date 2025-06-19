# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Test subpackage for OS mock classes used in unit tests for pyddcci.
Provides mock implementations for Windows monitor modules.
"""

import sys

sys.modules['app.ddcci.os.windows'] = sys.modules[__name__]

from . import monitor
sys.modules['app.ddcci.os.windows.monitor'] = monitor

from . import monitor_info
sys.modules['app.ddcci.os.windows.monitor_info'] = monitor_info

from . import monitor_list
sys.modules['app.ddcci.os.windows.monitor_list'] = monitor_list