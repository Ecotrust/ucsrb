from django.conf import settings
from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.auth.models import User
from features.registry import register
from features.models import MultiPolygonFeature
from scenarios.models import Scenario, PlanningUnit

GEOMETRY_DB_SRID = settings.GEOMETRY_DB_SRID

class FocusArea(models.Model):
    UNIT_TYPE_CHOICES = [
        ('HUC10', 'HUC10'),
        ('HUC12', 'HUC12'),
        ('RMU', 'RMU'),
        ('Pour Point', 'Pour Point')
    ]
    unit_type = models.CharField(max_length=20, null=True, blank=True, default=None, choices=UNIT_TYPE_CHOICES)

    # The HUC/RMU/PP ID
    unit_id = models.IntegerField(null=True, blank=True, default=None)

    geometry = gismodels.MultiPolygonField(srid=GEOMETRY_DB_SRID,
            null=True, blank=True, verbose_name="Focus Area Geometry")

    objects = gismodels.GeoManager()

class ScenarioState(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User)
    SCENARIO_TYPE_CHOICES = [
        ('Stream', 'Stream'),
        ('Forest', 'Forest'),
        ('Draw', 'Draw')
    ]
    scenario_type = models.CharField(max_length=10, choices=SCENARIO_TYPE_CHOICES)
    focus_area = models.ForeignKey(FocusArea, null=True, blank=True, default=None)#, models.SET_NULL)

@register
class TreatmentScenario(Scenario):
    scenario = models.ForeignKey(ScenarioState, null=True, blank=True, default=None)#, models.CASCADE)

    # Avoid Private land? (USE PUB_PRIV_OWN!)
    input_parameter_private_own = models.BooleanField(default=False)

    # pub_priv_own = models.CharField(max_length=255)         #PubPrivOwn
    OWNERSHIP_CHOICES = (
        # ('NULL', '---'),
        ('Bureau of Land Management', 'Bureau of Land Management'),
        ('Bureau of Reclamation', 'Bureau of Reclamation'),
        ('National Park Service', 'National Park Service'),
        ('Native American Land', 'Native American Land'),
        ('Private land', 'Private Land'),
        ('Public Land', 'Public Land'),
        ('U.S. Air Force', 'U.S. Air Force'),
        ('U.S. Army', 'U.S. Army'),
        ('U.S. Fish & Wildlife Service', 'U.S. Fish & Wildlife Service'),
        ('USDA Forest Service', 'USDA Forest Service'),
        ('Washington Department of Fish & Wildlife', 'Washington Department of Fish & Wildlife'),
        ('Washington Department of Forestry', 'Washington Department of Forestry'),
        ('Washington Department of Natural Resources', 'Washington Department of Natural Resources'),
        ('Washington Department of Parks and Recreation', 'Washington Department of Parks and Recreation'),
        ('Washington State Government', 'Washington State Government'),
    )
    # Target Land Ownership
    input_parameter_pub_priv_own = models.BooleanField(default=False)
    input_pub_priv_own = models.CharField(max_length=255, blank=True, null=True, choices=OWNERSHIP_CHOICES)

    # lsr_percent = models.FloatField()                       #LSRpct ("Late Successional Reserve")
    # Avoid Late Successional Reserve?
    input_parameter_lsr_percent = models.BooleanField(default=False)

    # has_critical_habitat = models.BooleanField(default=False) #CritHabLn
    # Avoid Critical Habitat?
    input_parameter_has_critical_habitat = models.BooleanField(default=False)

    # percent_roadless = models.FloatField()                  #IRApct ("Inventoried Roadless Area")
    # Avoid Inventoried Roadless Areas
    input_parameter_percent_roadless = models.BooleanField(default=False)

    # road_distance = models.FloatField()                     #RdDstEucMn ("Euclidean mean distance to roads")
    # Max distance from roads
    input_parameter_road_distance = models.BooleanField(default=False)
    input_max_road_distance = models.FloatField(null=True, blank=True, default=None)

    # percent_wetland = models.FloatField()                   #NWIwetpct
    # Avoid Wetlands?
    input_parameter_percent_wetland = models.BooleanField(default=False)

    # percent_riparian = models.FloatField()                  #NWIrippct
    # Avoid Riparian Areas?
    input_parameter_percent_riparian = models.BooleanField(default=False)

    # slope = models.FloatField()                             #SlopeMean
    # Max Slope
    input_parameter_slope = models.BooleanField(default=False)
    input_max_slope = models.FloatField(null=True, blank=True, default=False)

    # percent_fractional_coverage = models.FloatField()       #FrctCvg
    # Current Fractional Coverage
    input_parameter_percent_fractional_coverage = models.BooleanField(default=False)
    input_min_percent_fractional_coverage = models.FloatField(null=True, blank=True, default=False)
    input_max_percent_fractional_coverage = models.FloatField(null=True, blank=True, default=False)

    # percent_high_fire_risk_area = models.FloatField()       #HRFApct
    # Target High Fire Risk Areas
    input_parameter_percent_high_fire_risk_area = models.BooleanField(default=False)

    class Options:
        verbose_name = 'Treatment'
        # icon_url = 'marco/img/multi.png'
        form = 'ucsrb.forms.TreatmentScenarioForm'
        # form_template = 'scenarios/form.html'
        form_template = 'ucsrb_scenarios/form.html'
        show_template = 'scenarios/show.html'

class VegPlanningUnit(PlanningUnit):
    planning_unit_id = models.IntegerField()                #EtID
    veg_unit_id = models.IntegerField()                     #ID
    gridcode = models.IntegerField()                        #GRIDCODE
    # acres = models.FloatField()                            #acres
    acres = models.FloatField()                             #EtAcres
    huc_2_id = models.CharField(max_length=2)               #HUC_2
    huc_4_id = models.CharField(max_length=4)               #HUC_4
    huc_6_id = models.CharField(max_length=6)               #HUC_6
    huc_8_id = models.CharField(max_length=8)               #HUC_8
    huc_10_id = models.CharField(max_length=10)             #HUC_10
    huc_12_id = models.CharField(max_length=12)             #HUC_12
    pub_priv_own = models.CharField(max_length=255)         #PubPrivOwn
    lsr_percent = models.FloatField()                       #LSRpct
    has_critical_habitat = models.BooleanField(default=False) #CritHabLn
    percent_critical_habitat = models.FloatField()          #CritHabPly
    percent_roadless = models.FloatField()                  #IRApct ("Inventoried Roadless Area")
    percent_wetland = models.FloatField()                   #NWIwetpct
    percent_riparian = models.FloatField()                  #NWIrippct
    slope = models.FloatField()                             #SlopeMean
    road_distance = models.FloatField()                     #RdDstEucMn ("Euclidean mean distance to roads")
    percent_fractional_coverage = models.FloatField()       #FrctCvg
    percent_high_fire_risk_area = models.FloatField()       #HRFApct

    def is_private(self):
        return self.pub_priv_own == 'private'

    def has_roads(self):
        return self.percent_roadless < 100

    # def has_critical_habitat(self):
    #     return self.percent_critical_habitat > 0

    def has_high_fire_risk(self):
        return self.percent_high_fire_risk_area > 0

    vegetation_type = models.CharField(max_length=255, blank=True, null=True)
    forest_height = models.IntegerField()
    forest_class = models.CharField(max_length=255, blank=True, null=True)

    # canopy_coverage = models.IntegerField()
    # max_wind_speed = models.FloatField()
    #
    # majority_sediment = models.CharField(max_length=35, null=True, blank=True)  #LeaseBlock Update: might change back to IntegerField
    # variety_sediment = models.IntegerField()
    # is_private = models.BooleanField(default=False)
    # miles_from_road_access = models.IntegerField()
    # slope = models.IntegerField()
