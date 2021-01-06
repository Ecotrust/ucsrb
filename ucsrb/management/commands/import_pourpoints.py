from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = 'Import management pourpoints. 1 argument - a zipped shapefile in EPSG:3857'
    def add_arguments(self, parser):
        parser.add_argument('file',  type=str)

    def handle(self, *args, **options):
        import sys
        from io import StringIO, BytesIO
        import zipfile
        import shapefile
        from ucsrb.models import PourPoint

        # Check out Input
        try:
            in_file_name = options['file']
        except IndexError:
            self.stdout.write('--- ERROR: You must provide the location of the zipped shapefile and it\'s type! ---')
            sys.exit()
        if not zipfile.is_zipfile(in_file_name):
            self.stdout.write('--- ERROR: Input shapefile (1st arg) must be a zipfile ---')
            sys.exit()
        zip_format = None
        try:
            shape_zip = zipfile.ZipFile(in_file_name)
            zip_format = zipfile.ZIP_STORED
        except NotImplementedError:
            formats = [zipfile.ZIP_DEFLATED, zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA]
            for zipFormat in formats:
                try:
                    shape_zip = zipfile.ZipFile(in_file_name, compression=zipFormat)
                    zip_format = zipFormat
                    break
                except NotImplementedError:
                    pass
                except RuntimeError:
                    format_name = 'unknown'
                    if zipFormat == zipfile.ZIP_DEFLATED:
                        format_name = 'zlib'
                    if zipFormat == zipfile.ZIP_BZIP2:
                        format_name = 'bz2'
                    if zipFormat == zipfile.ZIP_LZMA:
                        format_name = 'lzma'
                    self.stdout.write('--- ERROR: Zipfile format not supported ---')
                    self.stdout.write('--- Please install: %s ---' % format_name)
                    sys.exit()
        if zip_format == None:
            self.stdout.write('--- ERROR: Unable to open zipfile ---')
            sys.exit()

        with zipfile.ZipFile(in_file_name, 'r', zip_format) as zipshape:
            shapefiles = [fname for fname in zipshape.namelist() if fname[-4:] == '.shp']
            dbffiles = [fname for fname in zipshape.namelist() if fname[-4:] == '.dbf']
            shxfiles = [fname for fname in zipshape.namelist() if fname[-4:] == '.shx']

            if len(shapefiles) != 1:
                if len(shapefiles) < 1:
                    self.stdout.write('--- ERROR: zipfile does not contain a .shp file ---')
                if len(shapefiles) > 1:
                    self.stdout.write('--- ERROR: zipfile contains multiple .shp files ---')
                sys.exit()
            if len(dbffiles) != 1:
                if len(dbffiles) < 1:
                    self.stdout.write('--- ERROR: zipfile does not contain a .dbf file ---')
                if len(dbffiles) > 1:
                    self.stdout.write('--- ERROR: zipfile contains multiple .dbf files ---')
                sys.exit()
            if len(shxfiles) != 1:
                if len(shxfiles) < 1:
                    self.stdout.write('--- ERROR: zipfile does not contain a .shx file ---')
                if len(shxfiles) > 1:
                    self.stdout.write('--- ERROR: zipfile contains multiple .shx files ---')
                sys.exit()

            shape = shapefile.Reader(
                        shp=BytesIO(zipshape.read(shapefiles[0])),
                        shx=BytesIO(zipshape.read(shxfiles[0])),
                        dbf=BytesIO(zipshape.read(dbffiles[0]))
                    )
            fieldsArray = [x[0] for x in shape.fields]

            ppt_IDIdx = fieldsArray.index('ppt_ID')-1

            id_field = 'ppt_ID'
            desc_field = None

            from django.contrib.gis.geos import GEOSGeometry, Point
            import json
            import_count = 0

            PourPoint.objects.all().delete()

            self.stdout.write('Writing new pour points...')
            for shapeRecord in shape.shapeRecords():
                if desc_field:
                    description = str(shapeRecord.record[unit_desc_index])
                else:
                    description = None
                shape_dict = shapeRecord.shape.__geo_interface__.copy()
                shape_dict['crs'] = settings.IMPORT_SRID
                geometry = GEOSGeometry(json.dumps(shape_dict))
                PourPoint.objects.create(
                    id = shapeRecord.record[ppt_IDIdx],
                    geometry = geometry
                )
                import_count += 1


        self.stdout.write('Successfully added %s Pour Points' % import_count)
