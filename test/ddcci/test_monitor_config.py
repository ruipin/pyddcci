# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from test import TestCase

from .os.mock import monitor_info
from app.ddcci.os import OS_MONITORS
from app.ddcci.monitor_config import MonitorConfig
from app.ddcci.monitor_filter import MonitorInfoMonitorFilter, OsMonitorMonitorFilter

class MonitorConfigTest(TestCase):
    def test_config(self):
        monitor_info.generate_mock_monitors(3, 0)
        monitor_info.MOCK_MONITORS[0].adapter.primary = True
        OS_MONITORS.enumerate()

        cfg1 = MonitorConfig(file_path=None)

        filter1 = OsMonitorMonitorFilter(OS_MONITORS[0])
        filter2 = OsMonitorMonitorFilter(OS_MONITORS[0])
        self.assertEqual(hash(filter1), hash(filter2))

        entry1 = cfg1.get(filter1)
        self.assertIn(entry1, cfg1)
        self.assertEqual(entry1, cfg1.get(filter1))
        self.assertIs(entry1, cfg1.get(filter1))

        entry1['bla'] = 'bla'
        self.assertEqual('bla', entry1['bla'])

        entry2 = cfg1.get(filter2)
        self.assertIs(entry2, entry1)
        self.assertEqual('bla', entry2['bla'])

        entry3 = cfg1.get(OS_MONITORS[0])
        self.assertIs(entry3, entry1)
        self.assertIs(entry3, entry2)
        self.assertEqual('bla', entry3['bla'])


        cfg2 = MonitorConfig(file_path=None)
        cfg2.load_from_list(cfg1.serialize())
        self.assertEqual(cfg1.serialize(), cfg2.serialize())

        entry4 = cfg2.get(filter1)
        self.assertEqual(entry4, entry1)
        self.assertEqual('bla', entry4['bla'])
