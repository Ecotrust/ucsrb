from django.db import models
from features.registry import register
from scenarios.models import Scenario, PlanningUnit

@register
class TreatmentScenario(Scenario):
    # input_max_distance_to_shore = models.FloatField(verbose_name='Maximum Distance to Shore', null=True, blank=True)
    #
    # input_parameter_substrate = models.BooleanField(verbose_name='Substrate Parameter', default=False)
    # input_substrate = models.ManyToManyField('Substrate', null=True, blank=True)

    ###
    # RDH 1/12/2018:
    # We need to track:
    # * ID
    # * Type (select, filter, or draw)
    # *
    #
    # We must be able to:
    # * Query by type
    # *
    #
    ####
    class Options:
        verbose_name = 'Treatment'
        # icon_url = 'marco/img/multi.png'
        form = 'ucsrb.forms.TreatmentScenarioForm'
        form_template = 'scenarios/form.html'
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
