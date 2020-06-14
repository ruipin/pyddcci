# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import unittest

# This is the class we want to test. So, we need to import it
from app.util.init import args



class ArgsTest(unittest.TestCase):
    def test_args_parser(self):
        parsed1 = args._PARSER.parse_args('-s XYZ 22 +no_verify 3 --get ABC 3 +raw'.split(' '))
        cmds1 = getattr(parsed1, 'app.cli.commands')
        self.assertEqual(len(cmds1), 2)
        self.assertFalse(cmds1[0]['args'].verify)
        self.assertTrue(cmds1[1]['args'].raw)

        with self.assertRaises(ValueError):
            args._PARSER.parse_args('-s XYZ +no_verify 3 --get ABC 3'.split(' '))



if __name__ == '__main__':
    unittest.main()