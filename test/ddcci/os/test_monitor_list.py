# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Unit tests for OsMonitorList in pyddcci.
Tests monitor enumeration and list behaviors using mock monitors.
"""

from test import TestCase

from app.ddcci.os import OsMonitorList
from test.ddcci.os.mock import monitor_info


class MonitorListTest(TestCase):
    def test_enumerate(self):
        # Create an OsMonitorList instance for testing
        monitors = OsMonitorList('Monitors')

        # Generate 3 mock monitors and save the current mock monitor list
        monitor_info.generate_mock_monitors(3, 0)
        old_mock_monitors = list(monitor_info.MOCK_MONITORS)

        # First enumeration: should detect 3 monitors
        monitors.enumerate()
        self.assertEqual(len(monitors), 3)
        old_monitors = monitors.aslist(recursive=False)

        # Second enumeration: should still detect 3 monitors (no change)
        monitors.enumerate()
        self.assertEqual(len(monitors), 3)

        # Check that all previously detected monitors are still connected and present
        for monitor in old_monitors:
            self.assertTrue(monitor.connected)
            self.assertIn(monitor, monitors)

        # Simulate a change: generate 2 new mock monitors and re-add one old monitor
        monitor_info.generate_mock_monitors(2, 1)
        monitor_info.MOCK_MONITORS.append(old_mock_monitors[0])

        # After enumeration, only 3 monitors should be present (2 new + 1 old)
        monitors.enumerate()
        self.assertEqual(len(monitors), 3)

        # The re-added old monitor should be connected and present
        self.assertTrue(old_monitors[0].connected)
        self.assertIn(old_monitors[0], monitors)
        # The other old monitors should be disconnected and not present
        for i in range(1, 3):
            self.assertFalse(old_monitors[i].connected)
            self.assertNotIn(old_monitors[i], monitors)