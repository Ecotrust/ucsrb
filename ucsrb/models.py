from django.db import models

from scenarios.models import Scenario, PlanningUnit

# class TreatmentScenario(Scenario):
    # input_max_distance_to_shore = models.FloatField(verbose_name='Maximum Distance to Shore', null=True, blank=True)
    #
    # input_parameter_substrate = models.BooleanField(verbose_name='Substrate Parameter', default=False)
    # input_substrate = models.ManyToManyField('Substrate', null=True, blank=True)

class VegPlanningUnit(PlanningUnit):
    # max_wind_speed = models.FloatField()
    #
    # majority_sediment = models.CharField(max_length=35, null=True, blank=True)  #LeaseBlock Update: might change back to IntegerField
    # variety_sediment = models.IntegerField()
    has_roads = models.BooleanField(default=False)
    has_endangered_habitat = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    has_high_fire_risk = models.BooleanField(default=False)
    miles_from_road_access = models.IntegerField()
    vegetation_type = models.CharField(max_length=255, blank=True, null=True)
    forest_height = models.IntegerField()
    forest_class = models.CharField(max_length=255, blank=True, null=True)
    slope = models.IntegerField()
    canopy_coverage = models.IntegerField()

# Create your models here.
