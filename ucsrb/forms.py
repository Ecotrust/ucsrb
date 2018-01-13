from ucsrb.models import *
# from features.forms import FeatureForm
from scenarios.forms import ScenarioForm
from django import forms
from django.forms.widgets import *
from analysistools.widgets import SliderWidget, DualSliderWidget

class HiddenScenarioBooleanField(forms.BooleanField):
    required=False,
    widget=CheckboxInput(
        attrs={
            'class': 'parameters hidden_checkbox'
        }
    )

class TreatmentScenarioForm(ScenarioForm):

    # 'acres': p_unit.acres,
    # 'huc_2_id': p_unit.huc_2_id,
    # 'huc_4_id': p_unit.huc_4_id,
    # 'huc_6_id': p_unit.huc_6_id,
    # 'huc_8_id': p_unit.huc_8_id,
    # 'huc_10_id': p_unit.huc_10_id,
    # 'huc_12_id': p_unit.huc_12_id,


    #
    # 'pub_priv_own': p_unit.pub_priv_own,
    # 'lsr_percent': p_unit.lsr_percent,
    # 'has_critical_habitat': p_unit.has_critical_habitat,
    # 'percent_critical_habitat': p_unit.percent_critical_habitat,
    # 'percent_roadless': p_unit.percent_roadless,
    # 'percent_wetland': p_unit.percent_wetland,
    # 'percent_riparian': p_unit.percent_riparian,
    # 'slope': p_unit.slope,
    # 'road_distance': p_unit.road_distance,
    # 'percent_fractional_coverage': p_unit.percent_fractional_coverage,
    # 'percent_high_fire_risk_area': p_unit.percent_high_fire_risk_area,

    # pub_priv_own = forms.BooleanField(
    #     label="Ownership",
    #     required=False,
    #     help_text="Type of ownership",
    #     widget=CheckboxInput(
    #
    #     )
    # )

    area = HiddenScenarioBooleanField(
        label="Area",
        help_text="Area of Planning Unit in sq. meters",
        # required=False,
        # widget=CheckboxInput(
        #     attrs={
        #         'class': 'parameters hidden_checkbox'
        #     }
        # )
    )
    area_min = forms.FloatField(
        required=False,
        initial=3500000000,
        widget=forms.TextInput(
            attrs={
                'class': 'slidervalue',
                'pre_text': 'Area'
            }
        )
    )
    area_max = forms.FloatField(
        required=False,
        initial=5500000000,
        widget=forms.TextInput(
            attrs={
                'class': 'slidervalue',
                'pre_text': 'to',
                'post_text': 'm<sup>2</sup>'
            }
        )
    )
    area_input = forms.FloatField(
        widget=DualSliderWidget(
            'area_min',
            'area_max',
            min=3000000000,
            max=6000000000,
            step=100000000
        )
    )

    def get_step_0_fields(self):
        names = [
            ('area', 'area_min', 'area_max', 'area_input'),
        ]
        return self._get_fields(names)

    def get_step_1_fields(self):
        names = []
        return self._get_fields(names)

    def get_steps(self):
        return self.get_step_0_fields(),

    class Meta(ScenarioForm.Meta):
        model = TreatmentScenario
        exclude = list(ScenarioForm.Meta.exclude)
        for f in model.output_fields():
            exclude.append(f.attname)
