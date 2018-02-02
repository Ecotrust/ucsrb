from django.core.management.base import BaseCommand, AppCommand
from optparse import make_option
from django.contrib.gis.geos import Polygon, MultiPolygon
from ucsrb.models import VegPlanningUnit


class Command(BaseCommand):

    #RDH Upgrade for django 1.10
    # see https://docs.djangoproject.com/en/1.11/howto/custom-management-commands/#accepting-optional-arguments
    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         '-a',
    #         '--all',
    #         action='store_true',
    #         dest='all',
    #         help="Enable sharing for ALL current groups",
    #     )

    def handle(self, *groupnames, **options):
        start_lon = -13471000
        start_lat = 6275000
        test_values = {
            'planning_unit_id': [0],
            'veg_unit_id': [0],
            'gridcode': [0],
            'acres': [0.0],
            'huc_2_id': [00],
            'huc_4_id': [0000],
            'huc_6_id': [000000],
            'huc_8_id': [00000000],
            'huc_10_id': [0000000000],
            'huc_12_id': [000000000000],
            # 'private_own': [True, False],
            'pub_priv_own': ['Private Land', 'Bureau of Land Management'],
            'lsr_percent': [5, 12],
            'has_critical_habitat': [True, False],
            'percent_critical_habitat': [5, 50],
            'percent_roadless': [5, 80],
            'road_distance': [1, 1000],
            'percent_wetland': [1, 80],
            'percent_riparian': [1, 80],
            'slope': [0, 50],
            'percent_fractional_coverage': [10, 50, 90],
            'percent_high_fire_risk_area': [0, 90],
            'vegetation_type': ['veg type'],
            'forest_height': [55],
            'forest_class': ['forest class']
        }
        init_values = {}
        for key in test_values.keys():
            init_values[key] = test_values[key][0]

        #TL Values
        current_lon = start_lon
        current_lat = start_lat
        max_cols = 55
        current_col = 0
        for (x, key_a) in enumerate(test_values.keys()):
            for (y, value_a) in enumerate(test_values[key_a]):
                insert_values = init_values
                insert_values[key_a] = test_values[key_a][y]
                for (x2, key) in enumerate(test_values.keys()):
                    for (y2, value) in enumerate(test_values[key]):
                        if not (y2 == y and x2 == x):
                            insert_values[key] = value
                            new_unit_poly = Polygon(
                                (
                                    (current_lon,current_lat),
                                    (current_lon+1000,current_lat),
                                    (current_lon+1000,current_lat-1000),
                                    (current_lon,current_lat-1000),
                                    (current_lon,current_lat)
                                )
                            )
                            insert_values['geometry'] = MultiPolygon(new_unit_poly,)
                            new_unit = VegPlanningUnit(**insert_values)
                            new_unit.save()
                            current_col = current_col+1
                            if current_col < max_cols:
                                current_lon = current_lon+1000
                            else:
                                current_col = 0
                                current_lon = start_lon
                                current_lat = current_lat - 1000
