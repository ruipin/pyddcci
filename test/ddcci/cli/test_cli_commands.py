# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import sys
from io import StringIO

from test import TestCase

from app.util.init import args
from app.cli.cli_commands import CliCommands
from test.ddcci.os.mock import monitor_info

class MonitorConfigTest(TestCase):
    def setUp(self):
        super().setUp()

        self.orig_stdout = sys.stdout
        self.stdout = StringIO()
        sys.stdout = self.stdout

    def assertStdoutEqual(self, msg):
        observed = self.stdout.getvalue()
        self.stdout.truncate(0)
        self.orig_stdout.write(observed)

        self.assertEqual(observed.strip(), msg.strip())

    def test_cli_commands(self):
        monitor_info.generate_mock_monitors(3,0)
        monitor_info.MOCK_MONITORS[0].adapter.primary = True

        cli_commands = CliCommands()
        parsed = args._PARSER.parse_args('-g primary input -s primary input hdmi1 -g primary input -s primary input dp1 -g primary input'.split(' '))
        cli_commands.from_argparse(getattr(parsed, 'app.cli.commands'))

        cli_commands.execute()
        self.assertStdoutEqual('0x0\nHDMI 1\nDP 1')


    def tearDown(self):
        super().tearDown()

        sys.stdout = self.orig_stdout
        print(self.stdout.getvalue())