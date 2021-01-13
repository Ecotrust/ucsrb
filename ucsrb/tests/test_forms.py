from django.test import TestCase

from ucsrb.forms import UploadShapefileForm

class UploadShapefileFormTest(TestCase):
    def test_zipped_shapefile_field_label(self):
        form = UploadShapefileForm()
        self.assertTrue(form.fields['zipped_shapefile'].label == 'Zipped Shapefile')

    def test_shp_projection_field_label(self):
        form = UploadShapefileForm()
        self.assertTrue(form.fields['shp_projection'].label == 'Shapefile Projection (Optional)')
