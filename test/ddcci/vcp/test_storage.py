# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import unittest

from app.ddcci.vcp.code.code_storage import VcpCodeStorage


class VcpStorageTest(unittest.TestCase):
    def test_storage(self):
        first = VcpCodeStorage(instance_name='first')
        second = VcpCodeStorage(instance_name='second')
        second.fallback = first

        first['apple'] = 0x12
        self.assertIn('apple', first)
        self.assertNotIn('apple', second)

        second['orange'] = 0x21
        self.assertNotIn('orange', first)
        self.assertIn('orange', second)

        first['apple']['TEN'] = 10
        self.assertIn('TEN', first['apple'])

        second.copy_storage(first)
        self.assertIn('apple', second)
        self.assertIn('TEN', second['apple'])

        second['apple']['TEN'].add_name('ONE_ZERO')
        self.assertNotIn('ONE_ZERO', first['apple'])
        self.assertIn('ONE_ZERO', second['apple'])

        second['apple']['FIFTY'] = 50
        self.assertNotIn('FIFTY', first['apple'])
        self.assertIn('FIFTY', second['apple'])

        first['apple']['TWENTY'] = 20
        self.assertIn('TWENTY', first['apple'])
        self.assertNotIn('TWENTY', second['apple'])

        second['apple']['TWENTY'] = None
        self.assertIn('TWENTY', first['apple'])
        self.assertNotIn('TWENTY', second['apple'])

        first['apple'].add_name('appl')
        self.assertIn('appl', first)
        self.assertNotIn('appl', second)



if __name__ == '__main__':
    unittest.main()