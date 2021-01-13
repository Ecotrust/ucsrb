from django.test import TestCase
from django.urls import reverse

from ucsrb.models import FocusArea, TreatmentScenario

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
