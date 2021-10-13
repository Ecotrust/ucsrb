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

class UploadShapefileForm(forms.Form):
    zipped_shapefile = forms.FileField(label='Zipped Shapefile')
    treatment_name = forms.CharField(max_length=255, required=False, label='Treatment Name')
    treatment_description = forms.CharField(max_length=255, required=False, label='Treatment Description')
    shp_projection = forms.CharField(max_length=255, required=False, label='Shapefile Projection (Optional)')
    prescription_treatment_selection = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(
            attrs={'class': 'prescription-choices'}
        ),
        choices= settings.PRESCRIPTION_TREATMENT_CHOICES,
        label='Select a default treatment prescription'
    )

class TreatmentScenarioForm(ScenarioForm):
    from ucsrb.models import FocusArea

    focus_area = HiddenScenarioBooleanField(
        label="Filter By Boundary",
        help_text="This should be true: ALWAYS",
        initial=True
    )

    focus_area_input = forms.IntegerField(
        label="Treatment Boundary",
        help_text="This should be invisible. Ppt Basin, HUC, or RMU Focus_Area ID",
        required=True,
    )

    private_own = HiddenScenarioBooleanField(
        label="Public Land Only",
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

    # percent_roadless = HiddenScenarioBooleanField(
    #     label="Avoid Roadless Area",
    #     help_text="Areas identified as 'roadless' in the Inventoried Roadless Areas",
    #     required=False,
    # )

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
                'class': 'slidervalue readonly-value',
                'readonly': 'readonly',
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
                'class': 'slidervalue readonly-value',
                'readonly': 'readonly',
                # 'pre_text': 'to',
                'post_text': '%'
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
        initial=0,
        widget=forms.TextInput(
            attrs={
                'class': 'slidervalue readonly-value',
                'pre_text': 'from',
                'readonly': 'readonly',
                'post_text': '%',
            }
        )
    )

    percent_fractional_coverage_max = forms.FloatField(
        required=False,
        initial=100,
        widget=forms.TextInput(
            attrs={
                'class': 'slidervalue readonly-value',
                'pre_text': 'to',
                'readonly': 'readonly',
                'post_text': '%',
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
        label="Target High Fire Risk Area",
        help_text="Only Treat Areas With High Fire Risk",
        required=False,
    )

    landform_type = HiddenScenarioBooleanField(
        label="Landform Type",
        help_text="Only treat certain types of geography",
        required=False,
    )

    landform_classes = (("0", "Include North Slopes"), ("1", "Inlcude South Slopes"), ("2", "Include Ridgetops"), ("3", "Include Valley Floors"), ("4", "Include East/West Slopes"))
    landform_type_checkboxes = forms.MultipleChoiceField(
        required=False,
        choices=landform_classes,
        widget=forms.CheckboxSelectMultiple(),
        initial=("0", "1", "2", "3", "4"),
        label="Land to include",
        help_text="Uncheck any topo types that you don't want included in your treatment",
    )

    # has_burned = HiddenScenarioBooleanField(
    #     # initial=False,
    #     label="Exclude areas burned in fire 2012-2018",
    #     help_text="Vegetation data is from 2012. It is not accurate for planning management impacts in areas that have burned since.",
    #     required=False,
    # )

    has_wilderness_area = HiddenScenarioBooleanField(
        initial=True,
        label="Exclude Wilderness Areas",
        help_text="Exclude Wilderness Areas",
        required=False,
    )

    # Prescriptions
    prescription_treatment_selection = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(
            attrs={'class': 'prescription-choices'}
        ),
        choices= settings.PRESCRIPTION_TREATMENT_CHOICES,
    )

    def get_step_0_fields(self):
        names = [
            ('focus_area', None, None, 'focus_area_input'),
            ('lsr_percent', None, None, None),
            # ('percent_roadless', None, None, None),
            ('pub_priv_own', None, None, 'pub_priv_own_input'),
            ('private_own', None, None, None),
            ('has_wilderness_area', None, None, None),
        ]
        return self._get_fields(names)

    def get_step_1_fields(self):
        names = [
            ('percent_riparian', None, None, None),
            ('percent_wetland', None, None, None),
            ('has_critical_habitat', None, None, None),
            # ('has_burned', None, None, None),
        ]
        return self._get_fields(names)

    def get_step_2_fields(self):
        names = [
            ('road_distance', None, 'road_distance_max', 'road_distance_input'),
            ('landform_type', None, None, None, 'landform_type_checkboxes'),
            (
                'percent_fractional_coverage',
                'percent_fractional_coverage_min',
                'percent_fractional_coverage_max',
                'percent_fractional_coverage_input'
            ),
            ('slope', None, 'slope_max', 'slope_input'),
            ('percent_high_fire_risk_area', None, None, None),
        ]
        return self._get_fields(names)

    def get_steps(self):
        return self.get_step_0_fields(), self.get_step_1_fields(), self.get_step_2_fields(),

    # def get_prescription_selection(self):
    #     names = [
    #         ('prescription_treatment_selection', None, None, None),
    #     ]
    #     return self._get_fields(names)

    def clean_focus_area_input(self):
        return FocusArea.objects.get(pk=self.cleaned_data['focus_area_input'])

    def is_valid(self, *args, **kwargs):
        if len(self.errors.keys()) == 1 and 'landform_type_checkboxes' in self.errors.keys() and len(self.errors['landform_type_checkboxes']) == 1 and 'is not one of the available choices.' in self.errors['landform_type_checkboxes'][0]:
            del self._errors['landform_type_checkboxes']
        return super(ScenarioForm, self).is_valid()

    def clean(self):

        checkbox_lookup = {
            '0': 'include_north',
            '1': 'include_south',
            '2': 'include_ridgetop',
            '3': 'include_floor',
            '4': 'include_east_west',
        }

        super(FeatureForm, self).clean()
        try:
            if 'landform_type_checkboxes' not in self.cleaned_data.keys() and self.cleaned_data['landform_type'] == True:
                checkdata = self.data.getlist('landform_type_checkboxes')
                checklist = False
                for box in checkdata:
                    if not box == 'False':
                        checklist = True
                        self.cleaned_data['landform_type_checkboxes'] = str([str(x) for x in box.split(',')])
                for landform_type_id in eval(self.cleaned_data['landform_type_checkboxes']):
                    landform_type = checkbox_lookup[landform_type_id]
                    self.cleaned_data['landform_type_checkboxes_%s' % landform_type] = True
                if not checklist:
                    self.data.__delitem__('landform_type_checkboxes')
        except Exception as e:
            print(e)
            pass
        return self.cleaned_data

    def save(self, commit=True):
        inst = super(TreatmentScenarioForm, self).save(commit=True)

        inst.aggregate_report = inst.aggregate_results()
        # if self.data.get('clear_support_file'):
        #     inst.support_file = None
        if commit:
            inst.save()
        return inst

    class Meta(ScenarioForm.Meta):
        model = TreatmentScenario
        exclude = list(ScenarioForm.Meta.exclude)
        for f in model.output_fields():
            exclude.append(f.attname)
        widgets = {}
