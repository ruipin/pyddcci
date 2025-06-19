# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Unit tests for LoggableMixin and related mixins in pyddcci.
Tests logging and combined mixin behaviors.
"""

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
        # Creating a class with wrong MRO should raise TypeError
        def _break(mixin):
            class cls(mixin, LoggableMixin):
                pass

            with self.assertRaises(TypeError):
                cls()

        _break(HierarchicalMixin)
        _break(NamedMixin)


    def test_simple(self):
        # Simple LoggableMixin instance
        a = L()
        self.assertIsNotNone(a.log)
        self.assertEqual(a.log.parent, logging.root)
        self.assertEqual(a.log.name, 'L')

        # LoggableNamedMixin instance
        b = LH()
        self.assertIsNotNone(b.log)
        self.assertEqual(b.log.parent, logging.root)
        self.assertEqual(b.log.name, 'LH')

        # LoggableHierarchicalNamedMixin instance with parent
        c = LHN(instance_name='b', instance_parent=b)
        self.assertIsNotNone(c.log)
        self.assertEqual(c.log.parent, b.log)
        self.assertEqual(c.log.name, 'LH.b')



if __name__ == '__main__':
    unittest.main()