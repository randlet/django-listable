from unittest import mock

from django.test import TestCase
from django.test.utils import override_settings
from listable.templatetags import listable


@override_settings(ROOT_URLCONF='listable_demo.urls')
class TestTags(TestCase):

    def test_default_header(self):
        self.assertEqual(listable.header("foo__bar_baz"), "Foo Bar Baz")

    def test_listable_url(self):
        request = mock.Mock()
        request.user.name = "username"
        results = listable.get_options({'request': request}, "staff-list")
        self.assertEqual(results['url'], '/staff-list/')

    def test_css_input_class(self):
        request = mock.Mock()
        request.user.name = "username"
        results = listable.get_options({'request': request}, "staff-list", css_input_class="test-class")
        self.assertEqual(results['cssInputClass'], 'test-class')

    def test_css_table_class(self):
        request = mock.Mock()
        request.user.name = "username"
        results = listable.get_options({'request': request}, "staff-list", css_table_class="test-class")
        self.assertEqual(results['cssTableClass'], 'test-class')
