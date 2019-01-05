from django.contrib import admin

from .models import *

from django.contrib.gis import admin as geoadmin
from django.contrib.gis.admin import GeoModelAdmin, OSMGeoAdmin

from accounts.models import EmailVerification, PasswordDictionary, UserData
from data_manager.models import AttributeInfo, DataNeed, Layer, LookupInfo, Theme
from drawing.models import AOI, WindEnergySite
from social_django.models import Association, Nonce, UserSocialAuth
from visualize.models import Bookmark, Content

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

admin.site.unregister(EmailVerification)
admin.site.unregister(PasswordDictionary)
admin.site.unregister(UserData)

admin.site.unregister(AttributeInfo)
admin.site.unregister(DataNeed)
admin.site.unregister(Layer)
admin.site.unregister(LookupInfo)
admin.site.unregister(Theme)

geoadmin.site.unregister(AOI)
geoadmin.site.unregister(WindEnergySite)

admin.site.unregister(Association)
admin.site.unregister(Nonce)
admin.site.unregister(UserSocialAuth)

admin.site.unregister(Bookmark)
admin.site.unregister(Content)

# class VegPlanningUnitAdmin(OSMGeoAdmin):
#     map_template = DATABASE_GEOGRAPHY['map_template']
