# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import unittest
import logging

# This is the class we want to test. So, we need to import it
from app.util.mixins import *


class L(LoggableMixin):
    pass

class LH(LoggableNamedMixin):
    pass

class LHN(LoggableHierarchicalNamedMixin):
    pass

class HierarchicalMixinsTest(unittest.TestCase):
    def test_fails_wrong_mro_order(self):
        def _break(mixin):
            class cls(mixin, LoggableMixin):
                pass

            with self.assertRaises(TypeError):
                cls()

        _break(HierarchicalMixin)
        _break(NamedMixin)


    def test_simple(self):
        # Simple
        a = L()
        self.assertIsNotNone(a.log)
        self.assertEqual(a.log.parent, logging.root)
        self.assertEqual(a.log.name, 'L')

        # Construct parent
        b = LH()
        self.assertIsNotNone(b.log)
        self.assertEqual(b.log.parent, logging.root)
        self.assertEqual(b.log.name, 'LH')

        # Construct child
        c = LHN(instance_name='b', instance_parent=b)
        self.assertIsNotNone(c.log)
        self.assertEqual(c.log.parent, b.log)
        self.assertEqual(c.log.name, 'LH.b')



if __name__ == '__main__':
    unittest.main()