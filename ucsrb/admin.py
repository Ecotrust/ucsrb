from django.contrib import admin

from .models import *

from django.contrib.gis import admin as geoadmin
from django.contrib.gis.admin import GeoModelAdmin, OSMGeoAdmin

class VegPlanningUnitAdmin(OSMGeoAdmin):
    list_display = ('pk', 'pub_priv_own', 'topo_height_class_majority')

class TreatmentScenarioAdmin(OSMGeoAdmin):
    list_display = ('name', 'user', 'description')

class FocusAreaAdmin(OSMGeoAdmin):
    list_display = ('unit_id', 'description', 'unit_type')

class PourPointAdmin(OSMGeoAdmin):
    list_display = ('id',)

# blatantly ripped off from Anatolij at https://stackoverflow.com/a/18559785/706797
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.db import models

from ckeditor.widgets import CKEditorWidget

class FlatPageCustom(FlatPageAdmin):
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageCustom)

geoadmin.site.register(VegPlanningUnit, VegPlanningUnitAdmin)
# geoadmin.site.register(TreatmentScenario, OSMGeoAdmin)
geoadmin.site.register(TreatmentScenario, TreatmentScenarioAdmin)
admin.site.register(ScenarioState)
geoadmin.site.register(FocusArea, FocusAreaAdmin)
geoadmin.site.register(PourPoint, PourPointAdmin)


# class VegPlanningUnitAdmin(OSMGeoAdmin):
#     map_template = DATABASE_GEOGRAPHY['map_template']
