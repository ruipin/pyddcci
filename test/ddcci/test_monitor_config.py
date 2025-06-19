# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Unit tests for the MonitorConfig class and monitor filter functionality in pyddcci.
Verifies configuration and filtering logic using mock monitors.
"""

from test import TestCase

from .os.mock import monitor_info
from app.ddcci.os import OS_MONITORS
from app.ddcci.monitor_config import MonitorConfig
from app.ddcci.monitor_filter import MonitorInfoMonitorFilter, OsMonitorMonitorFilter

class MonitorConfigTest(TestCase):
    def test_config(self):
        # Generate 3 mock monitors and set the first as primary
        monitor_info.generate_mock_monitors(3, 0)
        monitor_info.MOCK_MONITORS[0].adapter.primary = True
        OS_MONITORS.enumerate()

        # Create a MonitorConfig instance
        cfg1 = MonitorConfig(file_path=None)

        # Create two filters for the same monitor and check their hashes
        filter1 = OsMonitorMonitorFilter(OS_MONITORS[0])
        filter2 = OsMonitorMonitorFilter(OS_MONITORS[0])
        self.assertEqual(hash(filter1), hash(filter2))

        # Retrieve and check config entry for the filter
        entry1 = cfg1.get(filter1)
        self.assertIn(entry1, cfg1)
        self.assertEqual(entry1, cfg1.get(filter1))
        self.assertIs(entry1, cfg1.get(filter1))

        # Set and check a value in the config entry
        entry1['bla'] = 'bla'
        self.assertEqual('bla', entry1['bla'])

        # Retrieve the same entry using another filter and check identity
        entry2 = cfg1.get(filter2)
        self.assertIs(entry2, entry1)
        self.assertEqual('bla', entry2['bla'])

        # Retrieve the same entry using the monitor object and check identity
        entry3 = cfg1.get(OS_MONITORS[0])
        self.assertIs(entry3, entry1)
        self.assertIs(entry3, entry2)
        self.assertEqual('bla', entry3['bla'])

        # Serialize and reload config, then check equality
        cfg2 = MonitorConfig(file_path=None)
        cfg2.load_from_list(cfg1.serialize())
        self.assertEqual(cfg1.serialize(), cfg2.serialize())

        # Retrieve and check the entry from the reloaded config
        entry4 = cfg2.get(filter1)
        self.assertEqual(entry4, entry1)
        self.assertEqual('bla', entry4['bla'])
