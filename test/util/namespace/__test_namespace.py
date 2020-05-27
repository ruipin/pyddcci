import unittest

# This is the class we want to test. So, we need to import it
from app.util.mixins import *
from app.util.namespace import Namespace


class Ns(Namespace):
    pass

class NsName(Namespace, NamedMixin):
    pass

class NsHier(Namespace, HierarchicalMixin, NamedMixin):
    pass

class HierarchicalMixinsTest(unittest.TestCase):
    def test_fails_wrong_mro_order(self):
        def _break(mixin):
            class cls(mixin, Namespace):
                pass

            with self.assertRaises(TypeError):
                cls()

        _break(HierarchicalMixin)
        _break(NamedMixin)
        _break(LoggableMixin)

    def test_construct_simple(self):
        a = Hier()

        self.assertIsNone(a.instance_parent)

        self.assertEqual(str(a), "<Hier>")
        self.assertEqual(a.instance_hierarchy, "Hier")

        # Construct child
        b = Hier(instance_parent=a)

        self.assertIs(b.instance_parent, a)
        self.assertEqual(b.instance_hierarchy, "Hier.Hier")

        # Another child
        c = Hier(instance_parent=b)

        self.assertIs(c.instance_parent, b)
        self.assertEqual(c.instance_hierarchy, "Hier.Hier.Hier")

        # Test changing parent fails if it is not hierarchic
        with self.assertRaises(TypeError):
            b.instance_parent = 5

        # Change c's parent to a
        c.instance_parent = a

        self.assertIs(c.instance_parent, a)
        self.assertEqual(c.instance_hierarchy, "Hier.Hier")

    def test_construct_with_name(self):
        a = HierNamed(instance_name="name1")

        self.assertIsNone(a.instance_parent)

        self.assertEqual(str(a), "<HN:name1>")
        self.assertEqual(a.instance_hierarchy, "name1")

        # Construct child (no name)
        b = Hier(instance_parent=a)

        self.assertIs(b.instance_parent, a)
        self.assertEqual(b.instance_hierarchy, "name1.Hier")

        # Another child
        c = HierNamed(instance_parent=b, instance_name="name3")

        self.assertIs(c.instance_parent, b)
        self.assertEqual(str(c), "<HN:name3>")
        self.assertEqual(c.instance_hierarchy, "name1.Hier.name3")

        # Test changing parent fails if it is not hierarchic
        with self.assertRaises(TypeError):
            b.instance_parent = 5

        # Change c's parent to a
        c.instance_parent = a

        self.assertIs(c.instance_parent, a)
        self.assertEqual(c.instance_hierarchy, "name1.name3")



if __name__ == '__main__':
    unittest.main()