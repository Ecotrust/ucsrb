from django.contrib import admin

from .models import *

from django.contrib.gis import admin as geoadmin
from django.contrib.gis.admin import GeoModelAdmin, OSMGeoAdmin

class VegPlanningUnitAdmin(OSMGeoAdmin):
    list_display = ('pk', 'pub_priv_own', 'vegetation_type', 'forest_class')

geoadmin.site.register(VegPlanningUnit, VegPlanningUnitAdmin)
geoadmin.site.register(TreatmentScenario, OSMGeoAdmin)
admin.site.register(ScenarioState)
geoadmin.site.register(FocusArea, OSMGeoAdmin)


# class VegPlanningUnitAdmin(OSMGeoAdmin):
#     map_template = DATABASE_GEOGRAPHY['map_template']
