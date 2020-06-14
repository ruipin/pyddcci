# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import unittest

from app.util.init import args
args.is_unit_test = lambda: True

from app.util import CFG

from app.ddcci import monitor_config

class TestCase(unittest.TestCase):
    def setUp(self):
        CFG.app._default.test = True
        monitor_config.MONITOR_CONFIG = monitor_config.MonitorConfig(None)
