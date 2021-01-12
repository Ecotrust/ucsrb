from django.urls import resolve
from django.test import TestCase
from django.http import HttpRequest

from ucsrb.views import home

class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home)

    def test_home_returns_correct_html(self):
        request = HttpRequest()
        response = home(request)
        html = response.content.decode('utf8')
        self.assertTrue(html.startswith('\n<!DOCTYPE html>\n<html>'))
        self.assertIn('<title>UCSRB</title>', html)
        self.assertTrue(html.endswith('</html>\n'))
