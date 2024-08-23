from unittest.mock import Mock

from django.test import TestCase
from listable import utils
import pytest

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

    def test_unicode_unquote_2(self):
        assert utils.unquote_unicode("❤%EF%B8%8F Approved 😀", encoding="utf-8") == "❤️ Approved 😀"

    def test_unicode_unquote_3(self):
        assert utils.unquote_unicode("%u2764%uFE0F%20Approved%20%uD83D%uDE00", encoding="utf-8") == "❤️ Approved 😀"

    def test_unicode_unquote_4(self):
        assert utils.unquote_unicode("%F0%9F%91%8D%F0%9F%8F%BD%20%F0%9F%91%A9%E2%80%8D%F0%9F%91%A9%E2%80%8D%F0%9F%91%A7%E2%80%8D%F0%9F%91%A6%20%F0%90%8D%88%20%E2%AD%90%EF%B8%8F%20%C3%A9%20%E6%BC%A2%E5%AD%97%20%D9%85%D8%B1%D8%AD%D8%A8%D8%A7%20a%CC%81%20%E2%88%91%20%E2%80%94", encoding="utf-8") == "👍🏽 👩‍👩‍👧‍👦 𐍈 ⭐️ é 漢字 مرحبا á ∑ —"
