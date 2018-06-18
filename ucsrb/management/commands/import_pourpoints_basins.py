from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Import management pourpoint basins. 1 argument - a zipped shapefile in EPSG:3857'
    def add_arguments(self, parser):
        parser.add_argument('file',  type=str)

    def handle(self, *args, **options):
        import sys
        from io import StringIO, BytesIO
        import zipfile
        import shapefile
        from ucsrb.models import FocusArea, PourPointBasin

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

            shape = shapefile.Reader(shp=BytesIO(zipshape.read(shapefiles[0])),
                     shx=BytesIO(zipshape.read(shxfiles[0])),
                     dbf=BytesIO(zipshape.read(dbffiles[0])))
            fieldsArray = [x[0] for x in shape.fields]

            ppt_IDIdx = fieldsArray.index('ppt_ID')-1
            areaIdx = fieldsArray.index('area')-1
            mean_elevIdx = fieldsArray.index('mean_elev')-1
            avg_slpIdx = fieldsArray.index('avg_slp')-1
            slp_gt60Idx = fieldsArray.index('slp_gt60')-1
            elev_difIdx = fieldsArray.index('elev_dif')-1
            mean_shadeIdx = fieldsArray.index('mean_shade')-1
            veg_propIdx = fieldsArray.index('veg_prop')-1
            thc_11Idx = fieldsArray.index('thc_11')-1
            thc_12Idx = fieldsArray.index('thc_12')-1
            thc_13Idx = fieldsArray.index('thc_13')-1
            thc_14Idx = fieldsArray.index('thc_14')-1
            thc_15Idx = fieldsArray.index('thc_15')-1
            thc_21Idx = fieldsArray.index('thc_21')-1
            thc_22Idx = fieldsArray.index('thc_22')-1
            thc_23Idx = fieldsArray.index('thc_23')-1
            thc_24Idx = fieldsArray.index('thc_24')-1
            thc_25Idx = fieldsArray.index('thc_25')-1
            fc_11Idx = fieldsArray.index('fc_11')-1
            fc_12Idx = fieldsArray.index('fc_12')-1
            fc_13Idx = fieldsArray.index('fc_13')-1
            fc_14Idx = fieldsArray.index('fc_14')-1
            fc_15Idx = fieldsArray.index('fc_15')-1
            fc_21Idx = fieldsArray.index('fc_21')-1
            fc_22Idx = fieldsArray.index('fc_22')-1
            fc_23Idx = fieldsArray.index('fc_23')-1
            fc_24Idx = fieldsArray.index('fc_24')-1
            fc_25Idx = fieldsArray.index('fc_25')-1
            dwnst_pptIdx = fieldsArray.index('dwnst_ppt')-1

            in_type = 'PourPointDiscrete'
            id_field = 'ppt_ID'
            desc_field = None

            #fields has DeletionFlag as first item, not included in records indeces
            unit_id_index = fieldsArray.index(id_field) - 1

            from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon
            import json
            import_count = 0

            # Delete previous Focus Areas of given type
            self.stdout.write('Deleting all existing %s focus areas...' % in_type)
            FocusArea.objects.filter(unit_type=in_type).delete()

            self.stdout.write('Deleting all existing pour point basin records...')
            PourPointBasin.objects.all().delete()

            self.stdout.write('Writing new pour points and focus areas...')
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
                    geometry = multiGeometry
                )
                PourPointBasin.objects.create(
                    ppt_ID = shapeRecord.record[ppt_IDIdx],
                    area = shapeRecord.record[areaIdx],
                    mean_elev = int(shapeRecord.record[mean_elevIdx]),
                    avg_slp = int(shapeRecord.record[avg_slpIdx]),
                    slp_gt60 = shapeRecord.record[slp_gt60Idx],
                    elev_dif = shapeRecord.record[elev_difIdx],
                    mean_shade = int(shapeRecord.record[mean_shadeIdx]),
                    veg_prop = shapeRecord.record[veg_propIdx],
                    thc_11 = shapeRecord.record[thc_11Idx],
                    thc_12 = shapeRecord.record[thc_12Idx],
                    thc_13 = shapeRecord.record[thc_13Idx],
                    thc_14 = shapeRecord.record[thc_14Idx],
                    thc_15 = shapeRecord.record[thc_15Idx],
                    thc_21 = shapeRecord.record[thc_21Idx],
                    thc_22 = shapeRecord.record[thc_22Idx],
                    thc_23 = shapeRecord.record[thc_23Idx],
                    thc_24 = shapeRecord.record[thc_24Idx],
                    thc_25 = shapeRecord.record[thc_25Idx],
                    fc_11 = int(shapeRecord.record[fc_11Idx]),
                    fc_12 = int(shapeRecord.record[fc_12Idx]),
                    fc_13 = int(shapeRecord.record[fc_13Idx]),
                    fc_14 = int(shapeRecord.record[fc_14Idx]),
                    fc_15 = int(shapeRecord.record[fc_15Idx]),
                    fc_21 = int(shapeRecord.record[fc_21Idx]),
                    fc_22 = int(shapeRecord.record[fc_22Idx]),
                    fc_23 = int(shapeRecord.record[fc_23Idx]),
                    fc_24 = int(shapeRecord.record[fc_24Idx]),
                    fc_25 = int(shapeRecord.record[fc_25Idx]),
                    dwnst_ppt = shapeRecord.record[dwnst_pptIdx]
                )
                import_count += 1


        self.stdout.write('Successfully added %s Pour Point and Focus Area records (each)' % import_count)
