# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Unit tests for VcpCodeStorage in pyddcci.
Tests storage and fallback logic for VCP code storage.
"""

import unittest

from app.ddcci.vcp.code.code_storage import VcpCodeStorage


class VcpStorageTest(unittest.TestCase):
    def test_storage(self):
        # Create two VcpCodeStorage instances and set fallback
        first = VcpCodeStorage(instance_name='first')
        second = VcpCodeStorage(instance_name='second')
        second.fallback = first

        # Add a code to the first storage and check presence in both
        first['apple'] = 0x12
        self.assertIn('apple', first)
        self.assertNotIn('apple', second)

        # Add a code to the second storage and check presence in both
        second['orange'] = 0x21
        self.assertNotIn('orange', first)
        self.assertIn('orange', second)

        # Add a value to a code in the first storage and check
        first['apple']['TEN'] = 10
        self.assertIn('TEN', first['apple'])

        # Copy storage from first to second and check values
        second.copy_storage(first)
        self.assertIn('apple', second)
        self.assertIn('TEN', second['apple'])

        # Add a name to a value in the second storage and check isolation
        second['apple']['TEN'].add_name('ONE_ZERO')
        self.assertNotIn('ONE_ZERO', first['apple'])
        self.assertIn('ONE_ZERO', second['apple'])

        # Add a value to the second storage and check isolation
        second['apple']['FIFTY'] = 50
        self.assertNotIn('FIFTY', first['apple'])
        self.assertIn('FIFTY', second['apple'])

        # Add a value to the first storage and check isolation
        first['apple']['TWENTY'] = 20
        self.assertIn('TWENTY', first['apple'])
        self.assertNotIn('TWENTY', second['apple'])

        # Remove a value from the second storage and check
        second['apple']['TWENTY'] = None
        self.assertIn('TWENTY', first['apple'])
        self.assertNotIn('TWENTY', second['apple'])

        # Add a name to a code in the first storage and check isolation
        first['apple'].add_name('appl')
        self.assertIn('appl', first)
        self.assertNotIn('appl', second)



if __name__ == '__main__':
    unittest.main()