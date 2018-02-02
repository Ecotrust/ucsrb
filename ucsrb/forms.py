from ucsrb.models import *
from features.forms import FeatureForm
from scenarios.forms import ScenarioForm
from django import forms
from django.conf import settings
from django.forms.widgets import *
from analysistools.widgets import SliderWidget, DualSliderWidget

class HiddenScenarioBooleanField(forms.BooleanField):
    # initial=False,
    widget=CheckboxInput(
        attrs={
            'class': 'parameters hidden_checkbox'
        }
    )

class TreatmentScenarioForm(ScenarioForm):
    private_own = HiddenScenarioBooleanField(
        label="Avoid Private Land",
        help_text="Do not treat privately owned forest land",
        required=False,
    )

    pub_priv_own = HiddenScenarioBooleanField(
        label="Specific Land Ownership",
        help_text="Select land by owner",
        required=False,
    )

    pub_priv_own_input = forms.ChoiceField(
        required=False,
        widget=forms.Select(
            attrs={'class': 'parameters'}
        ),
        choices= settings.OWNERSHIP_CHOICES,
    )

    lsr_percent = HiddenScenarioBooleanField(
        label="Avoid L.S.R.",
        help_text="Protect Late Successional Reserve",
        required=False,
    )

    has_critical_habitat = HiddenScenarioBooleanField(
        label="Avoid Crit. Habitat",
        help_text="Protect Critical Habitat",
        required=False,
    )

    percent_roadless = HiddenScenarioBooleanField(
        label="Avoid Roadless Area",
        help_text="Areas identified as 'roadless' in the Inventoried Roadless Areas",
        required=False,
    )

    road_distance = HiddenScenarioBooleanField(
        label="Max Dist. From Roads",
        help_text="Set the maximum distance from roads to treat",
        required=False,
    )

    road_distance_max = forms.FloatField(
        required=False,
        initial=500,
        widget=forms.TextInput(
            attrs={
                'class': 'slidervalue',
                # 'pre_text': 'to',
                'post_text': 'meters'
            }
        )
    )

    road_distance_input = forms.FloatField(
        widget=SliderWidget(
            'road_distance_max',
            min=0,
            max=2000,
            step=100
        )
    )

    percent_wetland = HiddenScenarioBooleanField(
        label="Avoid Wetlands",
        help_text="Do not treat wetlands",
        required=False,
    )

    percent_riparian = HiddenScenarioBooleanField(
        label="Avoid Riparian Areas",
        help_text="Do not treat riparian areas",
        required=False,
    )

    slope = HiddenScenarioBooleanField(
        label="Max slope %",
        help_text="Set the maximum % slope to treat",
        required=False,
    )

    slope_max = forms.FloatField(
        required=False,
        initial=30,
        widget=forms.TextInput(
            attrs={
                'class': 'slidervalue',
                # 'pre_text': 'to',
                'post_text': 'miles'
            }
        )
    )

    slope_input = forms.FloatField(
        widget=SliderWidget(
            'slope_max',
            min=0,
            max=100,
            step=5
        )
    )

    percent_fractional_coverage = HiddenScenarioBooleanField(
        label="Fractional Coverage Range",
        help_text="Only Treat Given Fractional Coverage",
        required=False,
    )

    percent_fractional_coverage_min = forms.FloatField(
        required=False,
        initial=30,
        widget=forms.TextInput(
            attrs={
                'class': 'slidervalue',
                'pre_text': 'from',
                # 'post_text': 'miles'
            }
        )
    )

    percent_fractional_coverage_max = forms.FloatField(
        required=False,
        initial=100,
        widget=forms.TextInput(
            attrs={
                'class': 'slidervalue',
                'pre_text': 'to',
                'post_text': '%'
            }
        )
    )

    percent_fractional_coverage_input = forms.FloatField(
        widget=DualSliderWidget(
            'percent_fractional_coverage_min',
            'percent_fractional_coverage_max',
            min=0,
            max=100,
            step=5
        )
    )

    percent_high_fire_risk_area = HiddenScenarioBooleanField(
        label="Avoid High Fire Risk Area",
        help_text="Only Treat Areas With Lower Fire Risk",
        required=False,
    )

    def get_step_0_fields(self):
        names = [
            ('private_own', None, None, None),
            ('pub_priv_own', None, None, 'pub_priv_own_input'),
            ('lsr_percent', None, None, None),
            ('has_critical_habitat', None, None, None),
            ('percent_roadless', None, None, None),
            ('road_distance', None, 'road_distance_max', 'road_distance_input'),
            ('percent_wetland', None, None, None),
            ('percent_riparian', None, None, None),
            ('slope', None, 'slope_max', 'slope_input'),
            (
                'percent_fractional_coverage',
                'percent_fractional_coverage_min',
                'percent_fractional_coverage_max',
                'percent_fractional_coverage_input'
            ),
            ('percent_high_fire_risk_area', None, None, None),
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
        widgets = {}
