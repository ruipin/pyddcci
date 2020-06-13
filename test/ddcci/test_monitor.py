# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import unittest

from app.ddcci.monitor import Monitor
from .os.mock import monitor_info

class MonitorTest(unittest.TestCase):
    def test_change_input(self):

        monitor_info.generate_mock_monitors(3,0)
        monitor_info.MOCK_MONITORS[0].adapter.primary = True

        monitor1 = Monitor('Primary')

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



        monitor2 = Monitor('Hospital')
        monitor2['input'] = 'analog1'
        input4 = monitor2['input']
        self.assertNotEqual(input4, 'DP1')
        self.assertNotEqual(input4, 'hdmi1')
        self.assertNotEqual(input4, 'apple')
        self.assertEqual(input4, 'analog1')
        self.assertEqual(input4, 'rgb 1')

        with self.assertRaises(KeyError):
            monitor2['input'] = 'apple'

        self.assertEqual(input4, 'analog1')
        self.assertEqual(input4, 'rgb 1')


