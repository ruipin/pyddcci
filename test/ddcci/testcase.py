# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Base TestCase class for all pyddcci unit tests.
Sets up test configuration and environment for consistent test runs.
"""

import unittest

from app.ddcci import monitor_config

class TestCase(unittest.TestCase):
    def setUp(self):
        monitor_config.MONITOR_CONFIG = monitor_config.MonitorConfig(None)
