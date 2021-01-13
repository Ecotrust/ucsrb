from django.test import TestCase
from django.urls import reverse
from django.http import HttpRequest

from ucsrb.models import FocusArea, TreatmentScenario
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

class upload_treatment_shapefileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/ucsrb/upload_treatment_shapefile/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        request_url = '/ucsrb%s' % reverse('shp_upload')
        print('Requesting: %s ...' % request_url)
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, 200)
