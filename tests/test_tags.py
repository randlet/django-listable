from django.conf.urls import patterns, url
from django.views.generic import View
from django.test import TestCase
from django.test.utils import override_settings

from listable.templatetags import listable

import json

@override_settings(ROOT_URLCONF='listable_demo.urls')
class TestTags(TestCase):

    def test_default_header(self):
        self.assertEqual(listable.header("foo__bar_baz"), "Foo Bar Baz")

    def test_listable_url(self):
        results = listable.get_options({},"staff-list")
        self.assertEqual(results['url'], '/staff-list/')

    def test_css_input_class(self):
        results = listable.get_options({}, "staff-list", css_input_class="test-class")
        self.assertEqual(results['cssInputClass'], 'test-class')

    def test_css_table_class(self):
        results = listable.get_options({}, "staff-list", css_table_class="test-class")
        self.assertEqual(results['cssTableClass'], 'test-class')

