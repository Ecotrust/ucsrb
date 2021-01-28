import os, time
from selenium import webdriver

# https://selenium-python.readthedocs.io/waits.html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
            webdriver.DesiredCapabilities.FIREFOX["unexpectedAlertBehaviour"] = "accept"
            self.browser = webdriver.Firefox()
        except Exception as e:
            print(e)
            print("Have you installed xvfb?")
            print("Have you run `Xvfb :99 -ac &` since you last restarted?")
            print("Have you run `export DISPLAY=:99` since you last restarted?")
            quit()


    def tearDown(self):
        self.browser.quit()

    # Reminder: These literally have to start with the characters "test_"
    def test_anonymous_user_can_select_basin_to_define_treatment(self):
        print("Running Anonymous User Select Basin")
        print("TODO...")

    def test_registered_user_can_select_basin_to_define_treatment(self):
        print("Running Registered User Select Basin")
        print("TODO...")

    def test_anonymous_user_can_select_pour_point_to_define_treatment(self):
        print("Running Anonymous User Select Pour Point")
        print("TODO...")

    def test_registered_user_can_select_pour_point_to_define_treatment(self):
        print("Running Registered User Select Pour Point")
        print("TODO...")

    def test_anonymous_user_can_draw_polygon_to_define_treatment(self):
        print("Running Anonymous User Draw")
        print("TODO...")

    def test_registered_user_can_draw_polygon_to_define_treatment(self):
        print("Running Registered User Draw")
        print("TODO...")

    def test_registered_user_can_upload_a_shapefile_to_define_treatment(self):
        print("Running Registered User Upload")

        # Alice has a pre-existing shapefile of a plot she'd like to treat
        # She saved it to her hard drive
        self.assertTrue(os.path.exists('/usr/local/apps/marineplanner-core/apps/ucsrb/ucsrb/tests/test_files/multi-polygon/layers/'))
        file_name = 'multi-treatment'
        file_location = '/usr/local/apps/marineplanner-core/apps/ucsrb/ucsrb/tests/test_files/multi-polygon/layers/%s.zip' % file_name
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
        self.assertTrue(len(self.browser.find_elements_by_class_name("btn-method-upload")) == 1)
        self.browser.find_element_by_class_name("btn-method-define").click()
        self.browser.find_element_by_class_name("btn-method-upload").click()


        # Selects her file, names her treatment, and submits.
        # http://allselenium.info/file-upload-using-python-selenium-webdriver/#:~:text=Python%20Selenium%20Webdriver%20comes%20with,the%20file%20to%20be%20uploaded.
        self.browser.find_element_by_id("id_zipped_shapefile").send_keys(file_location)

        treatment_name = "Alice Test Treatment"
        self.browser.find_element_by_id("id_treatment_name").send_keys(treatment_name)

        # TODO: Test projection?

        self.browser.find_element_by_id("upload-treatment-form").find_element_by_id("upload-submit-btn").click()

        # She waits for the results to load
        print("Waiting up to 10 seconds for scenario to load...")
        try:
            element = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, "aggregate-results"))
            )
        except Exception as e:
            self.browser.quit()

        # She is then presented with a report regarding different results based on how she wishes to treat her treatment area.
        self.assertTrue(self.browser.find_element_by_id("results-nav").is_displayed())

        lt_20_pct_acres = self.browser.find_element_by_class_name("overflow-gradient").find_element_by_css_selector("table tr:nth-child(2) > td:nth-child(2)")
        self.assertEqual(lt_20_pct_acres.text, "333")

        # Why does Alice's define modal not disappear?
        if self.browser.find_element_by_id("define-modal").is_displayed():
            print("TODO: Figure out why Alice's 'Define' modal doesn't close itself")
            self.browser.find_element_by_id("define-modal").find_element_by_class_name("close").click()
            try:
                element = WebDriverWait(self.browser, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "modal-backdrop"))
                )
            except Exception as e:
                self.browser.quit()

        self.browser.find_element_by_css_selector("#results-nav button:nth-child(1)").click()
        self.assertTrue(self.browser.find_element_by_id("hydro-note").is_displayed())
        # How the heck are we going to get Alice to click on a pour point!?

        self.browser.find_element_by_id("nav-load-save").click()

        # In a moment of whimsy Alice deletes ALL of her saved treatments
        saved_treatments = self.browser.find_element_by_id("load-saved-list").find_elements_by_css_selector("li")
        for treatment in saved_treatments:
            print("Deleting %s..." % treatment.text)
            treatment.find_element_by_class_name("btn-trash").click()
            treatment.find_element_by_class_name("confirm-delete").click()
