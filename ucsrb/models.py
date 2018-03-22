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
    UNIT_TYPE_CHOICES = []
    for type in settings.FOCUS_AREA_TYPES:
        UNIT_TYPE_CHOICES.append((type, type))

    unit_type = models.CharField(max_length=20, null=True, blank=True, default=None, choices=UNIT_TYPE_CHOICES)

    # The HUC/RMU/PP ID
    unit_id = models.CharField(max_length=100, null=True, blank=True, default=None)

    description = models.CharField(max_length=255, null=True, blank=True, default=None)

    geometry = gismodels.MultiPolygonField(srid=GEOMETRY_DB_SRID,
            null=True, blank=True, verbose_name="Focus Area Geometry")

    objects = gismodels.GeoManager()

    def __str__(self):
        if self.description:
            return self.description
        else:
            return '%s: %s' % (self.unit_type, self.unit_id)

    def __unicode__(self):
        if self.description:
            return u'%s' % self.description
        else:
            return u'%s: %s' % (self.unit_type, self.unit_id)

class PourPointBasin(models.Model):
    ppt_ID = models.IntegerField(primary_key=True, verbose_name='Pour Point ID')
    area = models.FloatField(null=True, blank=True, default=None, verbose_name='Area in Acres')
    mean_elev = models.IntegerField(null=True, blank=True, default=None, verbose_name='Mean Elevation')
    avg_slp = models.FloatField(null=True, blank=True, default=None, verbose_name='Average Slope')
    slp_gt60 = models.IntegerField(default=0, verbose_name='Percent Area w/ Slope > 60%')
    elev_dif = models.IntegerField(null=True, blank=True, default=None, verbose_name='Elevation Difference in Meters')
    mean_shade = models.IntegerField(null=True, blank=True, default=None, verbose_name='Mean Shaded Area')
    veg_prop = models.IntegerField(null=True, blank=True, default=None, verbose_name='Percent Forested')
    thc_11 = models.IntegerField(verbose_name='Topo-Height Class 11')
    thc_12 = models.IntegerField(verbose_name='Topo-Height Class 12')
    thc_13 = models.IntegerField(verbose_name='Topo-Height Class 13')
    thc_14 = models.IntegerField(verbose_name='Topo-Height Class 14')
    thc_15 = models.IntegerField(verbose_name='Topo-Height Class 15')
    thc_21 = models.IntegerField(verbose_name='Topo-Height Class 21')
    thc_22 = models.IntegerField(verbose_name='Topo-Height Class 22')
    thc_23 = models.IntegerField(verbose_name='Topo-Height Class 23')
    thc_24 = models.IntegerField(verbose_name='Topo-Height Class 24')
    thc_25 = models.IntegerField(verbose_name='Topo-Height Class 25')
    fc_11 = models.IntegerField(verbose_name='Fractional Coverage 11')
    fc_12 = models.IntegerField(verbose_name='Fractional Coverage 12')
    fc_13 = models.IntegerField(verbose_name='Fractional Coverage 13')
    fc_14 = models.IntegerField(verbose_name='Fractional Coverage 14')
    fc_15 = models.IntegerField(verbose_name='Fractional Coverage 15')
    fc_21 = models.IntegerField(verbose_name='Fractional Coverage 21')
    fc_22 = models.IntegerField(verbose_name='Fractional Coverage 22')
    fc_23 = models.IntegerField(verbose_name='Fractional Coverage 23')
    fc_24 = models.IntegerField(verbose_name='Fractional Coverage 24')
    fc_25 = models.IntegerField(verbose_name='Fractional Coverage 25')
    dwnst_ppt = models.IntegerField(null=True, blank=True, default=None, verbose_name='Downstream Pourpoint ID')

    def __str__(self):
        return 'Pour Point Basin %s' % (self.ppt_ID)

    def __unicode__(self):
        return 'Pour Point Basin %s' % (self.ppt_ID)

class ClimateData(models.Model):
    ppt_id = models.IntegerField()
    datetime = models.DateTimeField(auto_now=False,auto_now_add=False)
    temp = models.IntegerField(verbose_name='temperature')
    pcp = models.IntegerField(verbose_name='precipitation')
    albedo = models.FloatField()
    wind = models.IntegerField()
    rh = models.FloatField(verbose_name='relative humidity')

    def __str__(self):
        return 'Climate for %s at %s' % (self.ppt_id, str(self.datetime))

    def __unicode__(self):
        return 'Climate for %s at %s' % (self.ppt_id, str(self.datetime))


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
        if self.focus_area_input:
            result = VegPlanningUnit.objects.filter(geometry__intersects=self.focus_area_input.geometry)
        else:
            result = VegPlanningUnit.objects.all()
        if result.count() > 0:
            return super(type(self), self).run(result)
        return result


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

# class Report(models.Model):
