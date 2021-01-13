import os, time
from selenium import webdriver
# import unittest

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.conf import settings

from ucsrb.local_settings import TESTING_USER, TESTING_PASSWORD
from ucsrb.models import TreatmentScenario
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
        file_name = 'small_polygon_treatment_4326'
        file_location = '/usr/local/apps/marineplanner-core/apps/ucsrb/ucsrb/tests/test_files/%s.zip' % file_name
        self.assertTrue(os.path.isfile(file_location))

        # She logs in to her SnowToFlow account...
        # client = Client()
        # client.login(username=TESTING_USER, password=TESTING_PASSWORD)
        self.browser.get("http://localhost:8000")
        self.browser.find_element_by_class_name("navbar-toggler").click()
        # Since test starts a new session, we can assume we're logged out.
        # try:
        #     if self.browser.find_element_by_id('sign-out').is_displayed():
        #         # session is logged in! Log out so we can continue!
        #         self.browser.find_element_by_id('sign-out').click()
        #         self.browser.find_element_by_class_name("navbar-toggler").click()
        # except Exception as e:
        #     pass
        self.browser.find_element_by_id('sign-in-modal').click()
        self.browser.find_element_by_id("id_login_email").send_keys(TESTING_USER)
        self.browser.find_element_by_id("id_login_password").send_keys(TESTING_PASSWORD)
        self.browser.find_element_by_class_name("sign-in").find_element_by_class_name("login-btn").click()

        # TODO: Remove this when fixed!
        print("TODO: on successful login, modal should close and app should launch!")
        self.browser.refresh()
        self.browser.find_element_by_id("launch").click()

        # Opens the upload form...
        self.assertTrue(len(self.browser.find_elements_by_id("upload-treatment-button")) == 1)
        self.browser.find_element_by_id("upload-treatment-button").click()

        # Selects her file and submits.
        # http://allselenium.info/file-upload-using-python-selenium-webdriver/#:~:text=Python%20Selenium%20Webdriver%20comes%20with,the%20file%20to%20be%20uploaded.
        self.browser.find_element_by_id("id_zipped_shapefile").send_keys(file_location)
        # TODO: Test projection?
        self.browser.find_element_by_id("upload-treatment-form").find_element_by_id("submit").click()

        # Her file is uploaded, unzipped and interpreted locally
        # These tests should probably live in test_views - Alice don't care.
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, "%s.shp" % file_name)))
        time.sleep(1)
        # Ater 1 second have we cleaned up?
        self.assertFalse(os.path.exists(os.path.join(settings.MEDIA_ROOT, "%s.shp" % file_name)))

        # She is then presented with a report regarding different results based on how she wishes to treat her treatment area.
        self.assertTrue(self.browser.find_element_by_id("results-nav").is_displayed())
        # TODO: test both Forest and Hydro data results.

        # In the meantime, her scenario is saved, but her uploaded files are removed
        # TODO: Test this in test_views.py
