# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from test import TestCase

from app.ddcci.monitor import Monitor
from .os.mock import monitor_info

class MonitorTest(TestCase):
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



    def test_capabilities(self):
        monitor_info.generate_mock_monitors(1, 0)
        monitor_info.MOCK_MONITORS[0].adapter.primary = True

        monitor1 = Monitor('Primary')
        monitor1.load_capabilities()

        values = monitor1.codes['input'].values
        self.assertEqual(4, len(values))
        self.assertEqual(4*2, len([x for x in values.names()]))
        self.assertEqual(4*3, len({x: y for x, y in values.items()}))


        # Export
        codes = monitor1._export_codes()
        self.assertEqual(23, len(codes))


    def test_codes_export(self):
        monitor_info.generate_mock_monitors(1, 0)
        monitor_info.MOCK_MONITORS[0].adapter.primary = True

        monitor1 = Monitor('Primary')
        self.assertIn('input', monitor1.codes)

        monitor1.codes['apple'] = 98
        self.assertIn('apple', monitor1.codes)

        self.assertIn('hdmi1', monitor1.codes['input'])
        monitor1.codes['input']['banana'] = 99
        self.assertIn('banana', monitor1.codes['input'])

        monitor1.export_codes()
        monitor1.import_codes()

        self.assertIn('apple', monitor1.codes)
        self.assertIn('input', monitor1.codes)
        self.assertIn('hdmi1', monitor1.codes['input'])
        self.assertIn('banana', monitor1.codes['input'])