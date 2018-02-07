from django.contrib import admin

from .models import *

from django.contrib.gis import admin as geoadmin
from django.contrib.gis.admin import GeoModelAdmin, OSMGeoAdmin

class VegPlanningUnitAdmin(OSMGeoAdmin):
    list_display = ('pk', 'pub_priv_own', 'vegetation_type', 'forest_class')

class TreatmentScenarioAdmin(OSMGeoAdmin):
    list_display = ('name', 'user', 'description')

class FocusAreaAdmin(OSMGeoAdmin):
    list_display = ('unit_id', 'unit_type')

geoadmin.site.register(VegPlanningUnit, VegPlanningUnitAdmin)
# geoadmin.site.register(TreatmentScenario, OSMGeoAdmin)
geoadmin.site.register(TreatmentScenario, TreatmentScenarioAdmin)
admin.site.register(ScenarioState)
geoadmin.site.register(FocusArea, FocusAreaAdmin)


# class VegPlanningUnitAdmin(OSMGeoAdmin):
#     map_template = DATABASE_GEOGRAPHY['map_template']
