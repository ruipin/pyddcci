# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from test import TestCase

from app.ddcci.os import OsMonitorList
from test.ddcci.os.mock import monitor_info


class MonitorListTest(TestCase):
    def test_enumerate(self):
        monitors = OsMonitorList('Monitors')

        monitor_info.generate_mock_monitors(3, 0)
        old_mock_monitors = list(monitor_info.MOCK_MONITORS)

        monitors.enumerate()
        self.assertEqual(len(monitors), 3)
        old_monitors = monitors.aslist(recursive=False)

        monitors.enumerate()
        self.assertEqual(len(monitors), 3)

        for monitor in old_monitors:
            self.assertTrue(monitor.connected)
            self.assertIn(monitor, monitors)

        monitor_info.generate_mock_monitors(2, 1)
        monitor_info.MOCK_MONITORS.append(old_mock_monitors[0])

        monitors.enumerate()
        self.assertEqual(len(monitors), 3)

        self.assertTrue(old_monitors[0].connected)
        self.assertIn(old_monitors[0], monitors)
        for i in range(1, 3):
            self.assertFalse(old_monitors[i].connected)
            self.assertNotIn(old_monitors[i], monitors)