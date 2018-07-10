from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Import Vegetation Planning Units. 1 argument - a directory or zipped shapefile in EPSG:3857 of the planning units'
    def add_arguments(self, parser):
        parser.add_argument('file',  type=str)

    def handle(self, *args, **options):
        import os, sys, zipfile, shapefile
        from io import StringIO, BytesIO
        from ucsrb.models import VegPlanningUnit

        is_zipfile = True

        # Check out Input
        try:
            in_file_name = options['file']
        except IndexError:
            self.stdout.write('--- ERROR: You must provide the location of the directory or zipped shapefile! ---')
            sys.exit()
        if not zipfile.is_zipfile(in_file_name):
            is_zipfile = False
            # self.stdout.write('--- ERROR: Input shapefile must be a zipfile ---')
            # sys.exit()

        if is_zipfile:
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
                # sys.exit()

            file_type = 'zipfile'
            with zipfile.ZipFile(in_file_name, 'r', zip_format) as zipshape:
                shapefiles = [fname for fname in zipshape.namelist() if fname[-4:] == '.shp']
                dbffiles = [fname for fname in zipshape.namelist() if fname[-4:] == '.dbf']
                shxfiles = [fname for fname in zipshape.namelist() if fname[-4:] == '.shx']
        else:
            file_type = 'directory'
            shapefiles = [fname for fname in os.listdir(in_file_name) if fname[-4:] == '.shp']
            dbffiles = [fname for fname in os.listdir(in_file_name) if fname[-4:] == '.dbf']
            shxfiles = [fname for fname in os.listdir(in_file_name) if fname[-4:] == '.shx']

        if len(shapefiles) != 1:
            if len(shapefiles) < 1:
                self.stdout.write('--- ERROR: %s does not contain a .shp file ---' % file_type)
            if len(shapefiles) > 1:
                self.stdout.write('--- ERROR: %s contains multiple .shp files ---' % file_type)
            sys.exit()
        if len(dbffiles) != 1:
            if len(dbffiles) < 1:
                self.stdout.write('--- ERROR: %s does not contain a .dbf file ---' % file_type)
            if len(dbffiles) > 1:
                self.stdout.write('--- ERROR: %s contains multiple .dbf files ---' % file_type)
            sys.exit()
        if len(shxfiles) != 1:
            if len(shxfiles) < 1:
                self.stdout.write('--- ERROR: %s does not contain a .shx file ---' % file_type)
            if len(shxfiles) > 1:
                self.stdout.write('--- ERROR: %s contains multiple .shx files ---' % file_type)
            sys.exit()

        if is_zipfile:
            with zipfile.ZipFile(in_file_name, 'r', zip_format) as zipshape:
                shape = shapefile.Reader(
                        shp=BytesIO(zipshape.read(shapefiles[0])),
                        shx=BytesIO(zipshape.read(shxfiles[0])),
                        dbf=BytesIO(zipshape.read(dbffiles[0]))
                )
        else:
            shape = shapefile.Reader('%s%s' % (in_file_name, shapefiles[0].split('.')[0]))
            #         shp='%s%s' % (in_file_name, shapefiles[0]),
            #         shx='%s%s' % (in_file_name, shxfiles[0]),
            #         dbf='%s%s' % (in_file_name, dbffiles[0])
            # )

        fieldsArray = [x[0] for x in shape.fields]

        planning_unit_id_index = fieldsArray.index('EtID') - 1
        veg_unit_id_index = fieldsArray.index('ID') - 1
        gridcode_index = fieldsArray.index('GRIDCODE') - 1
        # acres = models.FloatField()                            #acres
        acres_index = fieldsArray.index('EtAcres') - 1
        huc_2_id_index = fieldsArray.index('HUC_2') - 1
        huc_4_id_index = fieldsArray.index('HUC_4') - 1
        huc_6_id_index = fieldsArray.index('HUC_6') - 1
        huc_8_id_index = fieldsArray.index('HUC_8') - 1
        huc_10_id_index = fieldsArray.index('HUC_10') - 1
        huc_12_id_index = fieldsArray.index('HUC_12') - 1
        pub_priv_own_index = fieldsArray.index('PubPrivOwn') - 1
        lsr_percent_index = fieldsArray.index('LSRpct') - 1
        has_critical_habitat_index = fieldsArray.index('CritHabLn') - 1     #streams presence/absence (not % or proportion)
        percent_critical_habitat_index = fieldsArray.index('CritHabPly') - 1    #proportion of crit hab in veg unit
        percent_roadless_index = fieldsArray.index('IRApct') - 1
        percent_wetland_index = fieldsArray.index('NWIwetpct') - 1
        percent_riparian_index = fieldsArray.index('NWIrippct') - 1
        slope_index = fieldsArray.index('SlopeMean') - 1
        road_distance_index = fieldsArray.index('RdDstEucMn') - 1
        mean_fractional_coverage_index = fieldsArray.index('fczonmean') - 1         # actually mean fractional coverage (percent)
        percent_high_fire_risk_area_index = fieldsArray.index('WHPhvhPCT') - 1

        mgmt_allocation_code = fieldsArray.index('MgmtAlloca') - 1  # Forest Plan Land Management Allocation Code (for RMAs)
        mgmt_description = fieldsArray.index('MgmtDescri') - 1  # Forest Plan Land Management Description (for RMAs)
        rma_id_et = fieldsArray.index('FSmgt_etid') - 1  # Forest plan land management unique ID, created by Ecotrust
        ppt_id = fieldsArray.index('ppt_ID') - 1    # Nearest Downstream Pour Point Basin ID
        thc_zm = fieldsArray.index('thzonmaj') - 1  # Topo height class zonal majority

        # Ignore these if possible
        grid_id = fieldsArray.index('GRID_ID') - 1       # Hex ID for the fishnetting

        from django.contrib.gis.geos import GEOSGeometry, Polygon, MultiPolygon
        import json
        import_count = 0

        # Delete previous Focus Areas of given type
        self.stdout.write('Deleting all existing Veg Planning Units...')
        VegPlanningUnit.objects.all().delete()

        self.stdout.write('Writing new Veg Planning Units...')
        for shapeRecord in shape.shapeRecords():
            geometry = GEOSGeometry(json.dumps(shapeRecord.shape.__geo_interface__), srid=settings.IMPORT_SRID)
            if geometry.geom_type == 'Polygon':
                # multiGeometry = MultiPolygon((geometry))
                multiGeometry = geometry

                # elif geometry.geom_type == 'MultiPolygon':
                #     multiGeometry = geometry

                new_unit = VegPlanningUnit.objects.create(
                    planning_unit_id = shapeRecord.record[planning_unit_id_index],
                    veg_unit_id = shapeRecord.record[veg_unit_id_index],
                    gridcode = shapeRecord.record[gridcode_index],
                    acres = shapeRecord.record[acres_index],
                    huc_2_id = shapeRecord.record[huc_2_id_index],
                    huc_4_id = shapeRecord.record[huc_4_id_index],
                    huc_6_id = shapeRecord.record[huc_6_id_index],
                    huc_8_id = shapeRecord.record[huc_8_id_index],
                    huc_10_id = shapeRecord.record[huc_10_id_index],
                    huc_12_id = shapeRecord.record[huc_12_id_index],
                    pub_priv_own = shapeRecord.record[pub_priv_own_index],
                    lsr_percent = shapeRecord.record[lsr_percent_index],
                    has_critical_habitat = shapeRecord.record[has_critical_habitat_index],
                    percent_critical_habitat = shapeRecord.record[percent_critical_habitat_index],
                    percent_roadless = shapeRecord.record[percent_roadless_index],
                    percent_wetland = shapeRecord.record[percent_wetland_index],
                    percent_riparian = shapeRecord.record[percent_riparian_index],
                    slope = shapeRecord.record[slope_index],
                    road_distance = shapeRecord.record[road_distance_index],
                    percent_fractional_coverage = shapeRecord.record[mean_fractional_coverage_index],
                    percent_high_fire_risk_area = shapeRecord.record[percent_high_fire_risk_area_index],

                    # Fields to add to model
                    # mgmt_alloc_code = shapeRecord.record[mgmt_allocation_code],
                    # mgmt_description = shapeRecord.record[mgmt_description],
                    # mgmt_unit_id = shapeRecord.record[rma_id_et],
                    # dwnstream_ppt_id = shapeRecord.record[ppt_id],
                    # topo_height_class_majority = shapeRecord.record[thc_zm],

                    geometry = multiGeometry
                )

                # Stupid effing workaround:
                new_unit.mgmt_alloc_code = shapeRecord.record[mgmt_allocation_code]
                new_unit.mgmt_description = shapeRecord.record[mgmt_description]
                new_unit.mgmt_unit_id = shapeRecord.record[rma_id_et]
                new_unit.dwnstream_ppt_id = shapeRecord.record[ppt_id]
                new_unit.topo_height_class_majority = shapeRecord.record[thc_zm]

                import_count += 1
                new_unit.save()

                if import_count % 10000 == 0:
                    self.stdout.write('%s Planning Units Added...' % str(import_count))
                    pu_count = len(VegPlanningUnit.objects.all())
                    if not import_count == pu_count:
                        self.stdout.write('Only %d Planning Units Added after %d tries...' % (pu_count, import_count))
            else:
                # self.stdout.write('--- ERROR: Features in shapefile are not all (Multi)Polygons ---')
                # self.stdout.write('--- ERROR: Features in shapefile are not all Polygons ---')
                self.stdout.write('Discovered non-Polygon for record with Et_ID: %s' % str(shapeRecord.record[planning_unit_id_index]))
                # sys.exit()

        self.stdout.write('Successfully added %s Veg Planning Unit records' % import_count)
