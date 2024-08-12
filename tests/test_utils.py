from unittest.mock import Mock

from django.test import TestCase
from listable import utils

from staff.views import StaffList


class TestUtils(TestCase):

    def test_unique_order_preserved(self):
        self.assertListEqual(utils.unique([1, 1, 3, 2, 2]), [1, 3, 2])

    def test_lookup_dunder_prop(self):
        m = Mock()
        m.a.b.c = "foo"
        self.assertEqual(utils.lookup_dunder_prop(m, "a__b__c"), "foo")

    def test_class_for_view_name(self):
        self.assertIs(utils.class_for_view_name("staff-list"), StaffList)

    def test_unicode_unquote(self):
        assert utils.unquote_unicode("%u2714%uFE0F%20Approved", encoding="utf-8") == "✔️ Approved"

