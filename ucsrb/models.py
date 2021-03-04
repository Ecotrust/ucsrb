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

    objects = gismodels.Manager()

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

class PourPoint(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='Pour Point ID')
    geometry = gismodels.PointField(srid=GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Pour Point")

    imputed_ppt = models.ForeignKey('self', null=True, blank=True, default=None, verbose_name='Nearest Neighbor Match', on_delete=models.SET_NULL)
    streammap_id = models.IntegerField(null=True, blank=True, default=None)
    watershed_id = models.CharField(max_length=3, null=True, blank=True, default=None, choices=settings.WATERSHED_CHOICES, verbose_name="Modeled Watershed Identifier")
    confidence = models.IntegerField(default=0)

    objects = gismodels.Manager()

    def __str__(self):
        return 'Virtual Gauging Station Number %s' % (self.id)

    def __unicode__(self):
        return 'Virtual Gauging Station Number %s' % (self.id)

class ScenarioNNLookup(models.Model):
    ppt_id = models.IntegerField(verbose_name='Pour Point ID')
    # watershed_id = models.CharField(max_length=3, null=True, blank=True, default=None, choices=settings.WATERSHED_CHOICES, verbose_name="Modeled Watershed Identifier")
    scenario_id = models.IntegerField(verbose_name="Harvest Scenario Identifier")
    treatment_target = models.IntegerField()
    fc_delta = models.FloatField(verbose_name="Percent Change in Fractional Coverage")

    def __str__(self):
        return "Nearest Neighbor Pour Point %d, Scenario %d" % (self.ppt_id, self.scenario_id)

    def __unicode__(self):
        return "Nearest Neighbor Pour Point %d, Scenario %d" % (self.ppt_id, self.scenario_id)

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
    bulk_dens = models.FloatField(null=True, blank=True, default=None)
    cap_drv = models.FloatField(null=True, blank=True, default=None)
    exp_decrs = models.FloatField(null=True, blank=True, default=None)
    field_cap = models.FloatField(null=True, blank=True, default=None)
    lat_con = models.FloatField(null=True, blank=True, default=None)
    mannings = models.FloatField(null=True, blank=True, default=None)
    pore_sz = models.FloatField(null=True, blank=True, default=None)
    porosity = models.FloatField(null=True, blank=True, default=None)
    vert_con = models.FloatField(null=True, blank=True, default=None)
    wilt_pt = models.FloatField(null=True, blank=True, default=None)
    bbl_prsr = models.FloatField(null=True, blank=True, default=None)
    max_inf = models.FloatField(null=True, blank=True, default=None)
    center_x = models.IntegerField(null=True, blank=True, default=None)
    center_y = models.IntegerField(null=True, blank=True, default=None)
    normal_x = models.FloatField(null=True, blank=True, default=None)
    normal_y = models.FloatField(null=True, blank=True, default=None)
    normal_z = models.FloatField(null=True, blank=True, default=None)
    SDsphrical = models.FloatField(null=True, blank=True, default=None)

    def __str__(self):
        return 'Pour Point Basin %s' % (self.ppt_ID)

    def __unicode__(self):
        return 'Pour Point Basin %s' % (self.ppt_ID)

class ClimateData(models.Model):
    ppt_id = models.IntegerField()
    datetime = models.DateTimeField(auto_now=False,auto_now_add=False)
    temp = models.IntegerField(verbose_name='temperature')
    pcp = models.FloatField(verbose_name='precipitation')
    albedo = models.FloatField()
    wind = models.FloatField()
    rh = models.FloatField(verbose_name='relative humidity')

    def __str__(self):
        return 'Climate for %s at %s' % (self.ppt_id, str(self.datetime))

    def __unicode__(self):
        return 'Climate for %s at %s' % (self.ppt_id, str(self.datetime))

class ScenarioState(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    SCENARIO_TYPE_CHOICES = [
        ('Stream', 'Stream'),
        ('Forest', 'Forest'),
        ('Draw', 'Draw')
    ]
    scenario_type = models.CharField(max_length=10, choices=SCENARIO_TYPE_CHOICES)

@register
class TreatmentScenario(Scenario):
    focus_area = models.BooleanField(default=False)
    focus_area_input = models.ForeignKey(FocusArea, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    scenario = models.ForeignKey(ScenarioState, null=True, blank=True, default=None, on_delete=models.CASCADE)
    aggregate_report = models.TextField(null=True, blank=True, default=None)

    # Avoid Private land? (USE PUB_PRIV_OWN!)
    private_own = models.BooleanField(default=False)

    OWNERSHIP_CHOICES = settings.OWNERSHIP_CHOICES

    # Target Land Ownership
    pub_priv_own = models.BooleanField(default=False)                   #PubPrivOwn
    pub_priv_own_input = models.CharField(max_length=255, blank=True, null=True, default=None, choices=OWNERSHIP_CHOICES)

    # Avoid Late Successional Reserve?
    lsr_percent = models.BooleanField(default=False)                    #LSRpct ("Late Successional Reserve")

    # Avoid Critical Habitat?
    has_critical_habitat = models.BooleanField(default=False)           #CritHabLn

    # Avoid Inventoried Roadless Areas
    percent_roadless = models.BooleanField(default=False)               #IRApct ("Inventoried Roadless Area")

    # Max distance from roads
    road_distance = models.BooleanField(default=False)          #RdDstEucMn ("Euclidean mean distance to roads")
    road_distance_max = models.FloatField(null=True, blank=True, default=None)

    # Avoid Wetlands?
    percent_wetland = models.BooleanField(default=False)                #NWIwetpct

    # Avoid Riparian Areas?
    percent_riparian = models.BooleanField(default=False)               #NWIrippct

    # Max Slope
    slope = models.BooleanField(default=False)                          #SlopeMean
    slope_max = models.FloatField(null=True, blank=True, default=None)

    # Current Fractional Coverage
    percent_fractional_coverage = models.BooleanField(default=False)    #FrctCvg
    percent_fractional_coverage_min = models.FloatField(null=True, blank=True, default=None)
    percent_fractional_coverage_max = models.FloatField(null=True, blank=True, default=None)

    # Target High Fire Risk Areas
    percent_high_fire_risk_area = models.BooleanField(default=False)    #HRFApct

    # Filter by Landform type
    landform_type = models.BooleanField(default=False)
    landform_type_checkboxes_include_north = models.BooleanField(default=True)
    landform_type_checkboxes_include_south = models.BooleanField(default=True)
    landform_type_checkboxes_include_ridgetop = models.BooleanField(default=True)
    landform_type_checkboxes_include_floor = models.BooleanField(default=True)
    landform_type_checkboxes_include_east_west = models.BooleanField(default=True)
    landform_type_checkboxes = models.TextField(null=True, blank=True, default=None)

    # exclude Burned?
    has_burned = models.BooleanField(default=False)           #burn2012

    # Avoid Wilderness Areas?
    has_wilderness_area = models.BooleanField(default=True)           #Wilderness

    # Prescription (Rx) applied
    PRESCRIPTION_TREATMENT_CHOICES = settings.PRESCRIPTION_TREATMENT_CHOICES
    prescription_treatment_selection = models.CharField(max_length=255, null=True, blank=True, default=None, choices=PRESCRIPTION_TREATMENT_CHOICES)

    def run_filters(self, query):
        from ucsrb.views import run_filter_query
        filters = {}
        if self.focus_area_input:
            filters['focus_area'] = True
            if type(self.focus_area_input) == int:
                filters['focus_area_input'] = self.focus_area_input
            else:
                filters['focus_area_input'] = self.focus_area_input.pk

        if self.private_own:
            filters['private_own'] = True

        if self.pub_priv_own and self.pub_priv_own_input:
            filters['pub_priv_own'] = True
            filters['pub_priv_own_input'] = self.pub_priv_own_input

        if self.lsr_percent:
            filters['lsr_percent'] = True

        if self.has_critical_habitat:
            filters['has_critical_habitat'] = True

        # if self.percent_roadless:
        #     filters['percent_roadless'] = True

        if self.road_distance:
            filters['road_distance'] = True
            if self.road_distance_max:
                filters['road_distance_max'] = self.road_distance_max

        if self.percent_wetland:
            filters['percent_wetland'] = True

        if self.percent_riparian:
            filters['percent_riparian'] = True

        if self.slope:
            filters['slope'] = True
            if self.slope_max:
                filters['slope_max'] = self.slope_max

        if self.percent_fractional_coverage:
            filters['percent_fractional_coverage'] = True
            if self.percent_fractional_coverage_min:
                filters['percent_fractional_coverage'] = self.percent_fractional_coverage_min
            if self.percent_fractional_coverage_max:
                filters['percent_fractional_coverage_max'] = self.percent_fractional_coverage_max

        if self.percent_high_fire_risk_area:
            filters['percent_high_fire_risk_area'] = True

        if self.landform_type:
            filters['landform_type'] = self.landform_type
            filters['landform_type_include_north'] = self.landform_type_checkboxes_include_north
            filters['landform_type_include_south'] = self.landform_type_checkboxes_include_south
            filters['landform_type_include_ridgetop'] = self.landform_type_checkboxes_include_ridgetop
            filters['landform_type_include_floors'] = self.landform_type_checkboxes_include_floor
            filters['landform_type_include_east_west'] = self.landform_type_checkboxes_include_east_west

        if self.has_burned:
            filters['has_burned'] = True

        if self.has_wilderness_area:
            filters['has_wilderness_area'] = True

        (query, notes) = run_filter_query(filters)

        return query

    def run(self, result=None):
        if self.focus_area_input:
            result = VegPlanningUnit.objects.filter(geometry__intersects=self.focus_area_input.geometry)
        else:
            result = VegPlanningUnit.objects.all()
        if result.count() > 0:
            return super(type(self), self).run(result)
        return result

    def aggregate_results(self):
        vpus = self.run_filters(None) # There seems to be no need for passing a query here.
        # pu_ids = [int(x) for x in self.planning_units.split(',')]
        # vpus = VegPlanningUnit.objects.filter(pk__in=pu_ids)
        totals = {
            'Fractional Coverage': {
                '0-20%': 0,
                '20-40%': 0,
                '40-60%': 0,
                '60-80%': 0,
                '>80%': 0,
                'Total': 0
            },
            'Landforms': {
                'Ridgetops': 0,
                'Valley Bottoms': 0,
                'North Facing Slopes': 0,
                'South Facing Slopes': 0,
                'East or West Facing Slopes': 0
            },
            'Habitat Characteristics': {
                'Riparian Area': 0,
                'Wetlands': 0,
                'Critical Habitat': 0,
                # 'Salmon-Bearing Streams': 0,
                # 'Roadless Areas': 0
            }
        }
        for vpu in vpus:
            totals['Fractional Coverage']['Total'] += vpu.acres
            if vpu.percent_fractional_coverage <= 20:
                totals['Fractional Coverage']['0-20%'] += vpu.acres
            elif vpu.percent_fractional_coverage <= 40:
                totals['Fractional Coverage']['20-40%'] += vpu.acres
            elif vpu.percent_fractional_coverage <= 60:
                totals['Fractional Coverage']['40-60%'] += vpu.acres
            elif vpu.percent_fractional_coverage <= 80:
                totals['Fractional Coverage']['60-80%'] += vpu.acres
            else:
                totals['Fractional Coverage']['>80%'] += vpu.acres

            try:
                topo_class = int(str(vpu.topo_height_class_majority)[-1])
                if topo_class == 1:
                    totals['Landforms']['Ridgetops'] += vpu.acres
                if topo_class == 2:
                    totals['Landforms']['North Facing Slopes'] += vpu.acres
                if topo_class == 3:
                    totals['Landforms']['South Facing Slopes'] += vpu.acres
                if topo_class == 4:
                    totals['Landforms']['Valley Bottoms'] += vpu.acres
                if topo_class == 5:
                    totals['Landforms']['East or West Facing Slopes'] += vpu.acres
            except:
                pass

            totals['Habitat Characteristics']['Riparian Area'] += vpu.acres * vpu.percent_riparian * 0.01
            totals['Habitat Characteristics']['Wetlands'] += vpu.acres * vpu.percent_wetland * 0.01
            totals['Habitat Characteristics']['Critical Habitat'] += vpu.acres * vpu.percent_critical_habitat * 0.01
            # totals['Habitat Characteristics']['Roadless Areas'] += vpu.acres * vpu.percent_roadless * 0.01

        results = {
            'total_acres': int(totals['Fractional Coverage']['Total']),
            'results_list': [
                {'Forest Overstory Fractional Coverage': [
                    {'0-20% (acres)': int(totals['Fractional Coverage']['0-20%'])},
                    {'20-40% (acres)': int(totals['Fractional Coverage']['20-40%'])},
                    {'40-60% (acres)': int(totals['Fractional Coverage']['40-60%'])},
                    {'60-80% (acres)': int(totals['Fractional Coverage']['60-80%'])},
                    {'>80% (acres)': int(totals['Fractional Coverage']['>80%'])},
                    # {'Total Acres': int(totals['Fractional Coverage']['Total'])}
                    # {'Total Acres': total_treatment_acres}
                ]},
                    {'Landforms': [
                    {'Ridgetops (acres)': int(totals['Landforms']['Ridgetops'])},
                    {'Valley Bottoms (acres)': int(totals['Landforms']['Valley Bottoms'])},
                    {'North Facing Slopes (acres)': int(totals['Landforms']['North Facing Slopes'])},
                    {'South Facing Slopes (acres)': int(totals['Landforms']['South Facing Slopes'])},
                    {'East or West Facing Slopes (acres)': int(totals['Landforms']['East or West Facing Slopes'])}
                ]},
                    {'Habitat Characteristics': [
                    {'Riparian Area (acres)': int(totals['Habitat Characteristics']['Riparian Area'])},
                    {'Wetlands (acres)': int(totals['Habitat Characteristics']['Wetlands'])},
                    {'Critical Habitat (acres)': int(totals['Habitat Characteristics']['Critical Habitat'])},
                    # {'Salmon-Bearing Streams (mi)': 13},
                    # {'Roadless Areas (acres)': int(totals['Habitat Characteristics']['Roadless Areas'])}
                ]}
            ]
        }

        return results

    def set_report(self):
        self.aggregate_report = self.aggregate_results()
        self.save()

    @property
    def veg_units(self):
        if len(self.planning_units) == 0:  #empty result
            planninunit_ids = []
        else:
            planningunit_ids = [int(id) for id in self.planning_units.split(',')]
        planningunits = VegPlanningUnit.objects.filter(pk__in=planningunit_ids)
        return planningunits

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
    mgmt_alloc_code = models.CharField(max_length=255, null=True, blank=True, default=None)     #MgmtAlloca
    mgmt_description = models.CharField(max_length=255, null=True, blank=True, default=None)    #MgmtDescri
    mgmt_unit_id = models.IntegerField(null=True, blank=True, default=None)                     #FSmgt_etid
    dwnstream_ppt_id = models.IntegerField(null=True, blank=True, default=None)                 #ppt_ID
    topo_height_class_majority = models.IntegerField(null=True, blank=True, default=None)       #thzonmaj

    has_wilderness_area = models.BooleanField(default=False)    #Wilderness
    has_burned = models.BooleanField(default=False)             #burn2012

    # geometry = gismodels.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Veg Unit Geometry")
    geometry = gismodels.PolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Veg Unit Geometry")
    objects = gismodels.Manager()

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
class StreamFlowReading(models.Model):
    timestamp = models.CharField(max_length=30, verbose_name="Reading Timestamp")
    basin = models.ForeignKey(PourPointBasin, on_delete=models.CASCADE, verbose_name="Stream Segment Basin") # RDH 3/3/2021 -- Careful! This assumes we can derive basin from segment ID!
    metric = models.CharField(max_length=30, choices=settings.FLOW_METRIC_CHOICES, verbose_name="Measurement Metric")
    is_baseline = models.BooleanField(default=False, verbose_name="This is a baseline reading")
    treatment = models.ForeignKey(TreatmentScenario, null=True, blank=True, default=None, on_delete=models.CASCADE, verbose_name="Treatment Scenario")
    value = models.FloatField(verbose_name="Reading in m^3/hr")
