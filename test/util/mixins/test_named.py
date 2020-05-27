import unittest

# This is the class we want to test. So, we need to import it
from app.util.mixins.named import NamedMixin


class Named(NamedMixin):
    pass

class NamedMixinsTest(unittest.TestCase):
    def test_construct_no_name(self):
        a = Named()

        expected = Named.__name__
        self.assertEqual(a.instance_name, expected)
        self.assertEqual(str(a), f"<{expected}>")

    def test_construct_with_name(self):
        a = Named(instance_name="some")

        self.assertEqual(a.instance_name, "some")
        self.assertEqual(str(a), f"<N:some>")


if __name__ == '__main__':
    unittest.main()