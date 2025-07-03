"""
Unit tests for the Monitor class in pyddcci.
Tests monitor input changes and related monitor functionality using mock data.
"""
# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from test import TestCase

from app.ddcci.monitor import Monitor
from test.ddcci.os.mock import monitor_info

class MonitorTest(TestCase):
    def test_change_input(self):
        # Generate 3 mock monitors and set the first as primary
        monitor_info.generate_mock_monitors(3,0)
        monitor_info.MOCK_MONITORS[0].adapter.primary = True

        # Create a Monitor instance for the primary monitor
        monitor1 = Monitor('Primary')

        # Set input to 'dp1' and check various string representations and aliases
        monitor1['input'] = 'dp1'
        input1 = monitor1['input']
        self.assertEqual(input1, 'DP1')
        self.assertEqual(input1, 'dp1')
        self.assertEqual(input1, 'dp  1')
        self.assertEqual(input1, 'display PORT 1')
        self.assertNotEqual(input1, 'hdmi1')
        self.assertNotEqual(input1, 'HDMI1')
        self.assertNotEqual(input1, 'hdmi  1')
        self.assertNotEqual(input1, 'HD mi 1')

        # Change input to 'HDMI 1' and check aliases
        monitor1['input'] = 'HDMI 1'
        input2 = monitor1['input']
        self.assertNotEqual(input2, 'DP1')
        self.assertNotEqual(input2, 'dp1')
        self.assertNotEqual(input2, 'dp  1')
        self.assertNotEqual(input2, 'display PORT 1')
        self.assertEqual(input2, 'hdmi1')
        self.assertEqual(input2, 'HDMI1')
        self.assertEqual(input2, 'hdmi  1')
        self.assertEqual(input2, 'HD mi 1')

        # Add a custom input alias and test it
        monitor1.codes['input']['apple'] = 99
        monitor1.codes['input']['apple'].add_names('appl', 'APL')
        monitor1['input'] = 'APL'
        input3 = monitor1['input']
        self.assertNotEqual(input3, 'DP1')
        self.assertNotEqual(input3, 'dp1')
        self.assertNotEqual(input3, 'dp  1')
        self.assertNotEqual(input3, 'display PORT 1')
        self.assertNotEqual(input3, 'hdmi1')
        self.assertNotEqual(input3, 'HDMI1')
        self.assertNotEqual(input3, 'hdmi  1')
        self.assertNotEqual(input3, 'HD mi 1')
        self.assertEqual(input3, 'apple')
        self.assertEqual(input3, 'appl')
        self.assertEqual(input3, 'APL')
        self.assertEqual(input3, 99)

        # Test another monitor with a different input
        monitor2 = Monitor(monitor_info.MOCK_MONITORS[1]._model_words[1])
        monitor2['input'] = 'analog1'
        input4 = monitor2['input']
        self.assertNotEqual(input4, 'DP1')
        self.assertNotEqual(input4, 'hdmi1')
        self.assertNotEqual(input4, 'apple')
        self.assertEqual(input4, 'analog1')
        self.assertEqual(input4, 'rgb 1')

        # Setting an invalid value should raise KeyError
        with self.assertRaises(KeyError):
            monitor2['input'] = 'apple'

        # Ensure input remains unchanged after failed set
        self.assertEqual(input4, 'analog1')
        self.assertEqual(input4, 'rgb 1')

    def test_capabilities(self):
        # Generate a single mock monitor and set as primary
        monitor_info.generate_mock_monitors(1, 0)
        monitor_info.MOCK_MONITORS[0].adapter.primary = True

        # Create a Monitor instance and load its capabilities
        monitor1 = Monitor('Primary')
        monitor1.load_capabilities()

        # Check the number of input values and their aliases
        values = monitor1.codes['input'].values
        self.assertEqual(4, len(values))
        self.assertEqual(4*2, len([x for x in values.names()]))
        self.assertEqual(4*3, len({x: y for x, y in values.items()}))

        # Export monitor codes and check the number of exported codes
        codes = monitor1._export_codes()
        self.assertEqual(23, len(codes))

    def test_codes_export(self):
        # Generate a single mock monitor and set as primary
        monitor_info.generate_mock_monitors(1, 0)
        monitor_info.MOCK_MONITORS[0].adapter.primary = True

        # Create a Monitor instance and check code storage
        monitor1 = Monitor('Primary')
        self.assertIn('input', monitor1.codes)

        # Add a custom code and check its presence
        monitor1.codes['apple'] = 98
        self.assertIn('apple', monitor1.codes)

        # Add a custom input alias and check its presence
        self.assertIn('hdmi1', monitor1.codes['input'])
        monitor1.codes['input']['banana'] = 99
        self.assertIn('banana', monitor1.codes['input'])

        # Test export and import of codes
        monitor1.export_codes()
        monitor1.import_codes()

        self.assertIn('apple', monitor1.codes)
        self.assertIn('input', monitor1.codes)
        self.assertIn('hdmi1', monitor1.codes['input'])
        self.assertIn('banana', monitor1.codes['input'])