from django.conf import settings
from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.auth.models import User
from features.registry import register
from features.models import MultiPolygonFeature
# from scenarios.models import Scenario, PlanningUnit
from scenarios.models import Scenario

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

@register
class TreatmentScenario(Scenario):
    focus_area = models.BooleanField(default=False)
    focus_area_input = models.ForeignKey(FocusArea, null=True, blank=True, default=None)#, models.SET_NULL)
    # id = models.IntegerField(primary_key=True)
    scenario = models.ForeignKey(ScenarioState, null=True, blank=True, default=None)#, models.CASCADE)

    # Avoid Private land? (USE PUB_PRIV_OWN!)
    private_own = models.BooleanField(default=False)

    # pub_priv_own = models.CharField(max_length=255)         #PubPrivOwn
    OWNERSHIP_CHOICES = settings.OWNERSHIP_CHOICES

    # Target Land Ownership
    pub_priv_own = models.BooleanField(default=False)
    pub_priv_own_input = models.CharField(max_length=255, blank=True, null=True, default=None, choices=OWNERSHIP_CHOICES)

    # lsr_percent = models.FloatField()                       #LSRpct ("Late Successional Reserve")
    # Avoid Late Successional Reserve?
    lsr_percent = models.BooleanField(default=False)

    # has_critical_habitat = models.BooleanField(default=False) #CritHabLn
    # Avoid Critical Habitat?
    has_critical_habitat = models.BooleanField(default=False)

    # percent_roadless = models.FloatField()                  #IRApct ("Inventoried Roadless Area")
    # Avoid Inventoried Roadless Areas
    percent_roadless = models.BooleanField(default=False)

    # road_distance = models.FloatField()                     #RdDstEucMn ("Euclidean mean distance to roads")
    # Max distance from roads
    road_distance = models.BooleanField(default=False)
    road_distance_max = models.FloatField(null=True, blank=True, default=None)

    # percent_wetland = models.FloatField()                   #NWIwetpct
    # Avoid Wetlands?
    percent_wetland = models.BooleanField(default=False)

    # percent_riparian = models.FloatField()                  #NWIrippct
    # Avoid Riparian Areas?
    percent_riparian = models.BooleanField(default=False)

    # slope = models.FloatField()                             #SlopeMean
    # Max Slope
    slope = models.BooleanField(default=False)
    slope_max = models.FloatField(null=True, blank=True, default=None)

    # percent_fractional_coverage = models.FloatField()       #FrctCvg
    # Current Fractional Coverage
    percent_fractional_coverage = models.BooleanField(default=False)
    percent_fractional_coverage_min = models.FloatField(null=True, blank=True, default=None)
    percent_fractional_coverage_max = models.FloatField(null=True, blank=True, default=None)

    # percent_high_fire_risk_area = models.FloatField()       #HRFApct
    # Target High Fire Risk Areas
    percent_high_fire_risk_area = models.BooleanField(default=False)

    def run_filters(self, query):
        if self.focus_area_input:
            query = (query.filter(geometry__intersects=self.focus_area_input.geometry))

        if self.private_own:
            pu_ids = [pu.pk for pu in query if pu.pub_priv_own.lower() not in ['private land', 'private']]
            query = (query.filter(pk__in=pu_ids))

        if self.pub_priv_own and self.pub_priv_own_input:
            pu_ids = [pu.pk for pu in query if pu.pub_priv_own.lower() == self.pub_priv_own_input.lower()]
            query = (query.filter(pk__in=pu_ids))

        if self.lsr_percent:
            pu_ids = [pu.pk for pu in query if pu.lsr_percent < settings.LSR_THRESHOLD]
            query = (query.filter(pk__in=pu_ids))

        if self.has_critical_habitat:
            pu_ids = [pu.pk for pu in query if pu.percent_critical_habitat < settings.CRIT_HAB_THRESHOLD and not pu.has_critical_habitat]
            query = (query.filter(pk__in=pu_ids))

        if self.percent_roadless:
            pu_ids = [pu.pk for pu in query if pu.percent_roadless < settings.ROADLESS_THRESHOLD]
            query = (query.filter(pk__in=pu_ids))

        if self.road_distance:
            if self.road_distance_max:
                pu_ids = [pu.pk for pu in query if pu.road_distance <= self.road_distance_max]
                query = (query.filter(pk__in=pu_ids))

        if self.percent_wetland:
            pu_ids = [pu.pk for pu in query if pu.percent_wetland < settings.WETLAND_THRESHOLD]
            query = (query.filter(pk__in=pu_ids))

        if self.percent_riparian:
            pu_ids = [pu.pk for pu in query if pu.percent_riparian < settings.RIPARIAN_THRESHOLD]
            query = (query.filter(pk__in=pu_ids))

        if self.slope:
            if self.slope_max:
                pu_ids = [pu.pk for pu in query if pu.slope <= self.slope_max]
                query = (query.filter(pk__in=pu_ids))

        if self.percent_fractional_coverage:
            if self.percent_fractional_coverage_min:
                pu_ids = [pu.pk for pu in query if pu.percent_fractional_coverage >= self.percent_fractional_coverage_min]
                query = (query.filter(pk__in=pu_ids))
            if self.percent_fractional_coverage_max:
                pu_ids = [pu.pk for pu in query if pu.percent_fractional_coverage <= self.percent_fractional_coverage_max]
                query = (query.filter(pk__in=pu_ids))

        if self.percent_high_fire_risk_area:
            pu_ids = [pu.pk for pu in query if pu.percent_high_fire_risk_area < settings.FIRE_RISK_THRESHOLD]
            query = (query.filter(pk__in=pu_ids))

        return query

    def run(self, result=None):
        result = VegPlanningUnit.objects.all()
        return super(type(self), self).run(result)


    class Options:
        verbose_name = 'Treatment'
        # icon_url = 'marco/img/multi.png'
        form = 'ucsrb.forms.TreatmentScenarioForm'
        # form_template = 'scenarios/form.html'
        form_template = 'ucsrb_scenarios/form.html'
        show_template = 'scenarios/show.html'

class VegPlanningUnit(models.Model):
    # id = models.IntegerField(primary_key=True)
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

    vegetation_type = models.CharField(max_length=255, blank=True, null=True)
    forest_height = models.IntegerField()
    forest_class = models.CharField(max_length=255, blank=True, null=True)

    geometry = gismodels.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Veg Unit Geometry")
    objects = gismodels.GeoManager()

    def is_private(self):
        return self.pub_priv_own == 'private'

    def has_roads(self):
        return self.percent_roadless < 100

    def has_high_fire_risk(self):
        return self.percent_high_fire_risk_area > 0

    @property
    def kml_done(self):
        return """
        <Placemark id="%s">
            <visibility>1</visibility>
            <styleUrl>#%s-default</styleUrl>
            %s
        </Placemark>
        """ % ( self.uid, self.model_uid(),
                asKml(self.geometry.transform( settings.GEOMETRY_CLIENT_SRID, clone=True ))
              )
