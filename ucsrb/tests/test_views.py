from django.conf import settings
from django.http import HttpRequest
from django.test import TestCase
from django.urls import reverse, resolve

import json
import os

from ucsrb.models import FocusArea, TreatmentScenario
from ucsrb.views import home

class HomePageTest(TestCase):
    def test_home_view_kickoff(self):
        print("Testing Home View")

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

    def test_upload_treatment_shapefile_kickoff(self):
        print("Testing Treatment Shapefile Upload")

    # def test_view_url_exists_at_desired_location(self):
    #     response = self.client.get('/ucsrb/upload_treatment_shapefile/')
    #     self.assertEqual(response.status_code, 200)

    # def test_view_url_accessible_by_name(self):
    #     request_url = '/ucsrb%s' % reverse('shp_upload')
    #     print('Requesting: %s ...' % request_url)
    #     response = self.client.get(request_url)
    #     self.assertEqual(response.status_code, 200)

class ReportTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    # Report graphs were not showing for 'Change In Flow Rate'. This was due to
    # the view 'get_results_delta' not properly formatting the input for the
    # graph (the data had switched from dict to OrderedDict).
    # Given a 'flow_output' object, get_results_delta should return a dict
    # properly formatted to be ingested by the graph drawer.
    def test_233_delta_flow_report_format(self):
        from collections import OrderedDict
        from ucsrb.views import get_results_delta
        test_file_location = os.path.join(settings.BASE_DIR, '..', 'apps', 'ucsrb', 'ucsrb', 'tests', 'test_files','flow_data', 'flow_results_metw_3495.json')
        with open(test_file_location) as infile:
            data = json.load(infile)

        json_output = get_results_delta(data)
        ordered_output = OrderedDict({})
        for key in json_output.keys():
            ordered_output[key] = json_output[key]

        for output in [json_output, ordered_output]:
            print("Testing flow format: %s" % str(type(output)))
            self.assertIn('baseline', output.keys())
            for treatment in output.keys():
                self.assertEqual(type(output[treatment]), list)
                for reading in output[treatment]:
                    self.assertEqual(type(reading), dict)
                    self.assertIn('timestep', reading.keys())
                    self.assertEqual(type(reading['timestep']), str)
                    self.assertIn('flow', reading.keys())
                    self.assertEqual(type(reading['flow']), float)
