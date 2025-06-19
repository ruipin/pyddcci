# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Unit tests for HierarchicalMixin and related mixins in pyddcci.
Tests hierarchy and naming behaviors for custom mixin classes.
"""

import unittest

# This is the class we want to test. So, we need to import it
from app.util.mixins.hierarchical import HierarchicalMixin
from app.util.mixins.named import NamedMixin


class Hier(HierarchicalMixin):
    pass

class HierNamed(HierarchicalMixin, NamedMixin):
    pass

class NamedHier(NamedMixin, HierarchicalMixin):
    pass

class HierarchicalMixinsTest(unittest.TestCase):
    def test_fails_wrong_mro_order(self):
        # Creating NamedHier should fail due to incorrect MRO
        with self.assertRaises(TypeError):
            NamedHier()

    def test_construct_no_name(self):
        # Construct a root Hier instance
        a = Hier()
        self.assertIsNone(a.instance_parent)
        self.assertEqual(str(a), "<Hier>")
        self.assertEqual(a.instance_hierarchy, "Hier")

        # Construct a child Hier instance
        b = Hier(instance_parent=a)
        self.assertIs(b.instance_parent, a)
        self.assertEqual(b.instance_hierarchy, "Hier.Hier")

        # Construct another child
        c = Hier(instance_parent=b)
        self.assertIs(c.instance_parent, b)
        self.assertEqual(c.instance_hierarchy, "Hier.Hier.Hier")

        # Changing parent to a non-hierarchic object should fail
        with self.assertRaises(TypeError):
            b.instance_parent = 5

        # Change c's parent to a
        c.instance_parent = a
        self.assertIs(c.instance_parent, a)
        self.assertEqual(c.instance_hierarchy, "Hier.Hier")

    def test_construct_with_name(self):
        # Construct a root HierNamed instance with a name
        a = HierNamed(instance_name="name1")
        self.assertIsNone(a.instance_parent)
        self.assertEqual(str(a), "<HN name1>")
        self.assertEqual(a.instance_hierarchy, "name1")

        # Construct a child Hier instance
        b = Hier(instance_parent=a)
        self.assertIs(b.instance_parent, a)
        self.assertEqual(b.instance_hierarchy, "name1.Hier")

        # Construct another child with a name
        c = HierNamed(instance_parent=b, instance_name="name3")
        self.assertIs(c.instance_parent, b)
        self.assertEqual(str(c), "<HN name3>")
        self.assertEqual(c.instance_hierarchy, "name1.Hier.name3")

        # Changing parent to a non-hierarchic object should fail
        with self.assertRaises(TypeError):
            b.instance_parent = 5

        # Change c's parent to a
        c.instance_parent = a
        self.assertIs(c.instance_parent, a)
        self.assertEqual(c.instance_hierarchy, "name1.name3")



if __name__ == '__main__':
    unittest.main()