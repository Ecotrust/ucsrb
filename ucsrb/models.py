from celery.task.control import revoke
from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.auth.models import User
from django_celery_results.models import TaskResult
from features.registry import register
from features.models import MultiPolygonFeature
# from scenarios.models import Scenario, PlanningUnit
from scenarios.models import Scenario
from threading import Thread
from ucsrb.tasks import runTreatment
import json

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
    id = models.CharField(primary_key=True, max_length=30, verbose_name='Pour Point ID')
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

    @property
    def jobs(self):
        try:
            normal_job =  ModelRun.objects.get(scenario=self, weather_year=settings.NORMAL_YEAR_LABEL).task
        except Exception as e:
            normal_job = None
        try:
            wet_job =  ModelRun.objects.get(scenario=self, weather_year=settings.WET_YEAR_LABEL).task
        except Exception as e:
            wet_job = None
        try:
            dry_job =  ModelRun.objects.get(scenario=self, weather_year=settings.DRY_YEAR_LABEL).task
        except Exception as e:
            dry_job = None
        return {
            settings.NORMAL_YEAR_LABEL: normal_job,
            settings.WET_YEAR_LABEL: wet_job,
            settings.DRY_YEAR_LABEL: dry_job,
        }

    def job(self, weather_year=settings.NORMAL_YEAR_LABEL):
        return self.jobs[weather_year]

    def job_status(self, weather_year=settings.NORMAL_YEAR_LABEL):
        job = self.job(weather_year)
        if not job == None:
            return job.status
        else:
            return "None"

    def job_age(self, weather_year=settings.NORMAL_YEAR_LABEL):
        job = self.job(weather_year)
        if not job == None:
            return datetime.now() - job.date_created
        else:
            return 0

    def job_can_run(self, weather_year):
        job = self.job(weather_year)
        if job:
            if job.status == 'FAILURE':
                return True
            if hasattr(job, 'age') and job.age.total_seconds() > settings.MAX_DHSVM_RUN_DURATION:
                return True
        else:
            return True

        return False

    def run_dhsvm(self, force_rerun=False):
        jobs = self.jobs
        for weather_year in jobs.keys():
            job = jobs[weather_year]
            if force_rerun or self.job_can_run(weather_year):
                if job and job.task_id:
                    revoke(job.task_id, terminate=True)
                task = runTreatment.delay(self.id, weather_year)
                model_runs = ModelRun.objects.filter(scenario = self, weather_year = weather_year)
                if model_runs.count() > 0:
                    model_run = model_runs[0]
                    model_run.task_id = task.task_id
                    model_run.save()
                else:
                    model_run = ModelRun.objects.create(scenario = self, weather_year = weather_year, task_id=task.task_id)
            # else: viable job may yet run.

    def aggregate_results(self):
        vpus = self.run_filters(None) # There seems to be no need for passing a query here.
        full_vpus = vpus.filter(geometry__coveredby=self.focus_area_input.geometry)
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
            if vpu in full_vpus:
                vpu_acres = vpu.acres
            else:
                intersection = vpu.geometry.intersection(self.focus_area_input.geometry)
                intersection.transform(2163)
                vpu_acres = intersection.area/4046.86
            totals['Fractional Coverage']['Total'] += vpu_acres
            if vpu.percent_fractional_coverage <= 20:
                totals['Fractional Coverage']['0-20%'] += vpu_acres
            elif vpu.percent_fractional_coverage <= 40:
                totals['Fractional Coverage']['20-40%'] += vpu_acres
            elif vpu.percent_fractional_coverage <= 60:
                totals['Fractional Coverage']['40-60%'] += vpu_acres
            elif vpu.percent_fractional_coverage <= 80:
                totals['Fractional Coverage']['60-80%'] += vpu_acres
            else:
                totals['Fractional Coverage']['>80%'] += vpu_acres

            try:
                topo_class = int(str(vpu.topo_height_class_majority)[-1])
                if topo_class == 1:
                    totals['Landforms']['Ridgetops'] += vpu_acres
                if topo_class == 2:
                    totals['Landforms']['North Facing Slopes'] += vpu_acres
                if topo_class == 3:
                    totals['Landforms']['South Facing Slopes'] += vpu_acres
                if topo_class == 4:
                    totals['Landforms']['Valley Bottoms'] += vpu_acres
                if topo_class == 5:
                    totals['Landforms']['East or West Facing Slopes'] += vpu_acres
            except:
                pass

            totals['Habitat Characteristics']['Riparian Area'] += vpu_acres * vpu.percent_riparian * 0.01
            totals['Habitat Characteristics']['Wetlands'] += vpu_acres * vpu.percent_wetland * 0.01
            totals['Habitat Characteristics']['Critical Habitat'] += vpu_acres * vpu.percent_critical_habitat * 0.01
            # totals['Habitat Characteristics']['Roadless Areas'] += vpu_acres * vpu.percent_roadless * 0.01

        results = {
            'total_acres': int(totals['Fractional Coverage']['Total']),
            'results_list': [
                {'Forest Overstory Fractional Coverage': [
                    {'help': 'These values may not reflect areas burned or treated since 2012.'},
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
        self.run_dhsvm()

    def treatment_areas_geojson(self):
        tas = self.treatmentarea_set.all()
        ta_geojson_list = []
        for ta in tas:
            ta_geojson_list.append(ta.geojson)
        geojson_response = '{"type": "FeatureCollection","features": [%s]}' % ', '.join(ta_geojson_list)
        return geojson_response

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


class ModelRun(models.Model):
    WEATHER_YEAR_CHOICES = [(x, x) for x in settings.MODEL_YEARS.keys()]
    scenario = models.ForeignKey(TreatmentScenario, on_delete=models.CASCADE)
    weather_year = models.CharField(max_length=32, choices=WEATHER_YEAR_CHOICES)
    task_id = models.CharField(max_length=255)

    class Meta:
        unique_together = [['scenario', 'weather_year']]

    @property
    def task(self):
        try:
            return TaskResult.objects.get(task_id=self.task_id)
        except Exception as e:
            return None

    @property
    def task_status(self):
        if self.task:
            return task.status
        else:
            return None

class TreatmentArea(models.Model):
    # focus_area = models.ForeignKey(FocusArea, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    scenario = models.ForeignKey(TreatmentScenario, null=True, blank=True,
            default=None, on_delete=models.SET_NULL)
    # Prescription (Rx) applied
    PRESCRIPTION_TREATMENT_CHOICES = settings.PRESCRIPTION_TREATMENT_CHOICES
    prescription_treatment_selection = models.CharField(max_length=255,
            null=True, blank=True, default='notr',
            choices=PRESCRIPTION_TREATMENT_CHOICES)
    geometry = gismodels.PolygonField(srid=GEOMETRY_DB_SRID,
            null=True, blank=True, verbose_name="Treatment Area Geometry")

    objects = gismodels.Manager()

    @property
    def forested_acres(self):
        # vus = VegPlanningUnit.objects.filter(geometry__intersects=self.geometry)
        full_vus = VegPlanningUnit.objects.filter(geometry__coveredby=self.geometry)
        part_vus = VegPlanningUnit.objects.filter(geometry__overlaps=self.geometry)
        acres = 0
        for vu in full_vus:
            acres += vu.acres
        for vu in part_vus:
            intersection = vu.geometry.intersection(self.geometry)
            intersection.transform(2163)
            acres += intersection.area/4046.86

        return round(acres, 0)

    @property
    def total_acres(self):
        self.geometry.transform(2163)
        treatment_acres = int(round(self.geometry.area/4046.86, 0))
        # return geometry to web mercator
        self.geometry.transform(3857)
        return treatment_acres

    @property
    def geojson(self):
        out_geojson = {
            'type': "Feature",
            'geometry': json.loads(self.geometry.geojson),
            'properties': {
                'id': self.pk,
                'prescription': self.prescription_treatment_selection,
                'rx_label': settings.PRESCRIPTION_TREATMENT_CHOICES_LOOKUP[self.prescription_treatment_selection]['label'],
                'forested_acres': self.forested_acres,
                'total_acres': self.total_acres
            }
        }
        return json.dumps(out_geojson)

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
    percent_fractional_coverage = models.FloatField()       #fczonmean (was 'FrctCvg')
    percent_high_fire_risk_area = models.FloatField()       #WHPhvhPCT (was 'HRFApct')
    mgmt_alloc_code = models.CharField(max_length=255, null=True, blank=True, default=None)     #MgmtAlloca
    mgmt_description = models.CharField(max_length=255, null=True, blank=True, default=None)    #MgmtDescri
    mgmt_unit_id = models.IntegerField(null=True, blank=True, default=None)                     #FSmgt_etid
    dwnstream_ppt_id = models.CharField(max_length=30, null=True, blank=True, default=None)     #seg_id (was 'ppt_ID')
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
    time = models.DateTimeField(verbose_name="Reading DateTime")
    segment_id = models.CharField(max_length=30, blank=True, null=True, default=None, verbose_name="Streat Segment ID")
    metric = models.CharField(max_length=30, choices=settings.FLOW_METRIC_CHOICES, verbose_name="Measurement Metric")
    is_baseline = models.BooleanField(default=False, verbose_name="This is a baseline reading")
    treatment = models.ForeignKey(TreatmentScenario, null=True, blank=True, default=None, on_delete=models.CASCADE, verbose_name="Treatment Scenario")
    value = models.FloatField(verbose_name="Reading in m^3/hr")

    class Meta():
        indexes = [
            models.Index(fields=['segment_id']),
            models.Index(fields=['treatment']),
            models.Index(fields=['is_baseline'])
        ]
