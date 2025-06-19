# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Unit tests for NamedMixin in pyddcci.
Tests instance naming and string representation for NamedMixin.
"""

import unittest

# This is the class we want to test. So, we need to import it
from app.util.mixins.named import NamedMixin


class Named(NamedMixin):
    pass

class NamedMixinsTest(unittest.TestCase):
    def test_construct_no_name(self):
        # Construct a Named instance without a name
        a = Named()

        expected = Named.__name__
        self.assertEqual(a.instance_name, expected)  # Verify the instance name matches the class name
        self.assertEqual(str(a), f"<{expected}>")  # Verify the string representation matches the expected format

    def test_construct_with_name(self):
        # Construct a Named instance with a custom name
        a = Named(instance_name="some")

        self.assertEqual(a.instance_name, "some")  # Verify the instance name matches the provided name
        self.assertEqual(str(a), f"<N some>")  # Verify the string representation matches the expected format


if __name__ == '__main__':
    unittest.main()