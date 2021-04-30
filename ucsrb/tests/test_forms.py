import os, sys

from django.test import TestCase, Client
from django.conf import settings

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ucsrb.local_settings import TESTING_USER, TESTING_PASSWORD
from ucsrb.forms import UploadShapefileForm

class UploadShapefileFormTest(TestCase):
    def test_zipped_shapefile_field_label(self):
        form = UploadShapefileForm()
        self.assertTrue(form.fields['zipped_shapefile'].label == 'Zipped Shapefile')

    def test_shp_projection_field_label(self):
        form = UploadShapefileForm()
        self.assertTrue(form.fields['shp_projection'].label == 'Shapefile Projection (Optional)')

class FeaturecCollectionTest(TestCase):
    def setUp(self):
        try:
            webdriver.DesiredCapabilities.FIREFOX["unexpectedAlertBehaviour"] = "accept"
            self.browser = webdriver.Firefox()
            self.selenium.implicitly_wait(5)
        except Exception as e:
            print(e)
            print("Have you installed xvfb?")
            print("Have you run `Xvfb :99 -ac &` since you last restarted?")
            print("Have you run `export DISPLAY=:99` since you last restarted?")
            sys.exit(1)

    def tearDownClass(self):
        self.selenium.quit()

    def test_form_entry(self):
        # Test name: Draw Form 2
        # Step # | name | target | value
        # 1 | open | / |
        self.selenium.get("http://localhost:8111/")
        # 2 | setWindowSize | 1680x1025 |
        self.selenium.set_window_size(1680, 1025)
        # 3 | click | id=launch |
        self.selenium.find_element(By.ID, "launch").click()
        # 4 | click | css=.btn-method-define |
        self.selenium.find_element(By.CSS_SELECTOR, ".btn-method-define").click()
        # 5 | click | css=.btn-method-draw |
        self.selenium.find_element(By.CSS_SELECTOR, ".btn-method-draw").click()
        # 6 | click | css=.ol-unselectable:nth-child(1) |
        self.selenium.find_element(By.CSS_SELECTOR, ".ol-unselectable:nth-child(1)").click()
        # 7 | click | css=.ol-unselectable:nth-child(1) |
        self.selenium.find_element(By.CSS_SELECTOR, ".ol-unselectable:nth-child(1)").click()
        # 8 | click | css=.ol-unselectable:nth-child(1) |
        self.selenium.find_element(By.CSS_SELECTOR, ".ol-unselectable:nth-child(1)").click()
        # 9 | click | css=.ol-unselectable:nth-child(1) |
        self.selenium.find_element(By.CSS_SELECTOR, ".ol-unselectable:nth-child(1)").click()
        # 10 | click | css=.ol-unselectable:nth-child(1) |
        self.selenium.find_element(By.CSS_SELECTOR, ".ol-unselectable:nth-child(1)").click()
        # 11 | doubleClick | css=.ol-unselectable:nth-child(1) |
        element = self.selenium.find_element(By.CSS_SELECTOR, ".ol-unselectable:nth-child(1)")
        actions = ActionChains(self.selenium)
        actions.double_click(element).perform()
        # 12 | click | css=.ol-unselectable:nth-child(1) |
        self.selenium.find_element(By.CSS_SELECTOR, ".ol-unselectable:nth-child(1)").click()
        # 13 | click | css=.ol-unselectable:nth-child(1) |
        self.selenium.find_element(By.CSS_SELECTOR, ".ol-unselectable:nth-child(1)").click()
        # 14 | click | css=.ol-unselectable:nth-child(1) |
        self.selenium.find_element(By.CSS_SELECTOR, ".ol-unselectable:nth-child(1)").click()
        # 15 | click | css=.ol-unselectable:nth-child(1) |
        self.selenium.find_element(By.CSS_SELECTOR, ".ol-unselectable:nth-child(1)").click()
        # 16 | doubleClick | css=.ol-unselectable:nth-child(1) |
        element = self.selenium.find_element(By.CSS_SELECTOR, ".ol-unselectable:nth-child(1)")
        actions = ActionChains(self.selenium)
        actions.double_click(element).perform()
        # 17 | click | name=treat_name |
        self.selenium.find_element(By.NAME, "treat_name").click()
        # 18 | type | name=treat_name | Draw Test
        self.selenium.find_element(By.NAME, "treat_name").send_keys("Draw Test")
        # 19 | type | name=treat_desc | Draw Test
        self.selenium.find_element(By.NAME, "treat_desc").send_keys("Draw Test")
        self.assertTrue(self.selenium.find_element(By.NAME, "featurecollection").value != "")
