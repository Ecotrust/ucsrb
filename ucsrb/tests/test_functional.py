from selenium import webdriver
# import unittest
from django.test import TestCase
import os

from django.test import Client
from ucsrb.local_settings import TESTING_USER, TESTING_PASSWORD
#
# class HomePageLoadsTest(TestCase):
#     def setUp(self):
#         self.browser = webdriver.Firefox()
#
#     def tearDown(self):
#         self.browser.quit()
#
#     def test_browser_title(self):
#         print("Running HomePageLoadsTest")
#         self.browser.get('http://localhost:8000')
#         self.assertIn('UCSRB', self.browser.title)
#         # self.fail('Finish the test!');

class RegisteredUserTest(TestCase):
    def setUp(self):
        try:
            self.browser = webdriver.Firefox()
        except Exception as e:
            print(e)
            print("Have you installed xvfb?")
            print("Have you run `Xvfb :99 -ac &` since you last restarted?")
            print("Have you run `export DISPLAY=:99` since you last restarted?")
            quit()


    def tearDown(self):
        self.browser.quit()

    # Reminder: This listerally has to start with the word "test_"
    def test_registered_user_can_upload_a_shapefile_to_define_treatment(self):
        print("Running RegisteredUserTest")

        # Alice has a pre-existing shapefile of a plot she'd like to treat
        # She saved it to her hard drive
        self.assertTrue(os.path.exists('/usr/local/apps/marineplanner-core/apps/ucsrb/ucsrb/tests/test_files/'))
        self.assertTrue(os.path.isfile('/usr/local/apps/marineplanner-core/apps/ucsrb/ucsrb/tests/test_files/small_polygon_treatment_4326.zip'))

        # She logs in to her SnowToFlow account...
        client = Client()
        client.login(username=TESTING_USER, password=TESTING_PASSWORD)

        # Opens the upload form...
        upload_form = client.get('/.../')

        # Selects her file and submits.

        # Her form is uploaded and interpreted locally

        # She is then presented witha report regarding different results based on how she wishes to treat her treatment area.

        # In the meantime, her scenario is saved, but her uploaded files are removed

# if __name__ == '__main__':
#     unittest.main(warnings='ignore')
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "../../../marineplanner/settings")
    # os.environ['DJANGO_SETTINGS_MODULE'] = "../../../marineplanner/settings"
    # from django.test import Client
    # from django.conf import settings
