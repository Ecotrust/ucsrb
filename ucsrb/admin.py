from django.contrib import admin

from .models import *

from django.contrib.gis import admin as geoadmin
from django.contrib.gis.admin import GeoModelAdmin, OSMGeoAdmin
geoadmin.site.register(VegPlanningUnit, OSMGeoAdmin)
geoadmin.site.register(TreatmentScenario, OSMGeoAdmin)


# class VegPlanningUnitAdmin(OSMGeoAdmin):
#     map_template = DATABASE_GEOGRAPHY['map_template']
