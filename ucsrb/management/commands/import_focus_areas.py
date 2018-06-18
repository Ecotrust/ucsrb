from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Import management boundaries. 2 arguments - a zipped shapefile in EPSG:3857 and a layer type matching one of: %s' % str(settings.FOCUS_AREA_TYPES)
    def add_arguments(self, parser):
        parser.add_argument('file',  type=str)
        parser.add_argument('type',  type=str)

    def handle(self, *args, **options):
        import sys
        from io import StringIO, BytesIO
        import zipfile
        import shapefile
        from ucsrb.models import FocusArea

        # Check out Input
        try:
            in_file_name = options['file']
            in_type = options['type']
        except IndexError:
            self.stdout.write('--- ERROR: You must provide the location of the zipped shapefile and it\'s type! ---')
            sys.exit()
        if in_type not in settings.FOCUS_AREA_TYPES:
            self.stdout.write('--- ERROR: Input type (2nd arg) must be one of the following: ---')
            self.stdout.write('--- %s ---' % settings.FOCUS_AREA_TYPES)
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

            shape = shapefile.Reader(shp=BytesIO(zipshape.read(shapefiles[0])),
                     shx=BytesIO(zipshape.read(shxfiles[0])),
                     dbf=BytesIO(zipshape.read(dbffiles[0])))
            fieldsArray = [x[0] for x in shape.fields]

            # TODO: Define id_fields for all supported in_types!
            id_field = None
            desc_field = None
            if in_type == 'HUC10':
                id_field = 'HUC_10'
                desc_field = 'HU_10_Name'
            if in_type == 'HUC12':
                id_field = 'HUC_12'
                desc_field = 'HU_12_NAME'
            if in_type == 'RMU':
                id_field = None
            # if in_type == 'PourPoint':
            #     id_field = 'ppt_ID'
            if in_type == 'PourPointOverlap':
                id_field = 'ppt_ID'
            if in_type == 'PourPointDiscrete':
                id_field = 'ppt_ID'

            if not id_field:
                self.stdout.write('--- ERROR: ID Field unknown. Check your file type argument. ---')
                sys.exit()

            #fields has DeletionFlag as first item, not included in records indeces
            unit_id_index = fieldsArray.index(id_field) - 1
            if desc_field:
                unit_desc_index = fieldsArray.index(desc_field) -1

            from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon
            import json
            import_count = 0

            # Delete previous Focus Areas of given type
            self.stdout.write('Deleting all existing %s focus areas...' % in_type)
            FocusArea.objects.filter(unit_type=in_type).delete()

            self.stdout.write('Writing new %s focus areas...' % in_type)
            for shapeRecord in shape.shapeRecords():
                unit_id = shapeRecord.record[unit_id_index]
                if desc_field:
                    description = str(shapeRecord.record[unit_desc_index])
                else:
                    description = None
                geometry = GEOSGeometry(json.dumps(shapeRecord.shape.__geo_interface__), srid=settings.IMPORT_SRID)
                if geometry.geom_type == 'Polygon':
                    multiGeometry = MultiPolygon((geometry))
                elif geometry.geom_type == 'MultiPolygon':
                    multiGeometry = geometry
                else:
                    self.stdout.write('--- ERROR: Features in shapefile are not all (Multi)Polygons ---')
                    sys.exit()
                FocusArea.objects.create(
                    unit_type = in_type,
                    unit_id = str(unit_id),
                    description = description,
                    geometry = multiGeometry,
                )
                import_count += 1


        self.stdout.write('Successfully added %s Focus Area records' % import_count)
