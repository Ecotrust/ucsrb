from ucsrb.models import *
from features.forms import FeatureForm
# from scenarios.forms import ScenarioForm
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

class TreatmentScenarioForm(FeatureForm):
    input_parameter_private_own = HiddenScenarioBooleanField(
        label="Avoid Private Land",
        help_text="Do not treat privately owned forest land",
        required=False,
    )

    input_parameter_pub_priv_own = HiddenScenarioBooleanField(
        label="Specific Land Ownership",
        help_text="Select land by owner",
        required=False,
    )

    input_pub_priv_own = forms.ChoiceField(
        required=False,
        widget=forms.Select(
            attrs={'class': 'parameters'}
        ),
        choices= settings.OWNERSHIP_CHOICES,
    )

    input_parameter_lsr_percent = HiddenScenarioBooleanField(
        label="Avoid L.S.R.",
        help_text="Protect Late Successional Reserve",
        required=False,
    )

    input_parameter_has_critical_habitat = HiddenScenarioBooleanField(
        label="Avoid Crit. Habitat",
        help_text="Protect Critical Habitat",
        required=False,
    )

    def get_step_0_fields(self):
        names = [
            ('input_parameter_private_own', None, None, None),
            ('input_parameter_pub_priv_own', None, None, 'input_pub_priv_own'),
            ('input_parameter_lsr_percent', None, None, None),
            ('input_parameter_has_critical_habitat', None, None, None),
        ]
        return self._get_fields(names)

    def get_step_1_fields(self):
        names = []
        return self._get_fields(names)

    def get_steps(self):
        # return self.get_step_0_fields(), self.get_step_1_fields(),
        return self.get_step_0_fields(),

    def _get_fields(self, names):
        fields = []
        for name_list in names:
            group = []
            for name in name_list:
                if name:
                    group.append(self[name])
                else:
                    group.append(None)
            while len(group) < 5:
                group.append(None)
            fields.append(group)
        return fields

    def is_valid(self, *args, **kwargs):
        return super(FeatureForm, self).is_valid()

    def clean(self):
        super(FeatureForm, self).clean()
        return self.cleaned_data

    def save(self, commit=True):
        inst = super(FeatureForm, self).save(commit=False)
        if self.data.get('clear_support_file'):
            inst.support_file = None
        if commit:
            inst.save()
        return inst

    class Meta(FeatureForm.Meta):
        model = TreatmentScenario
        exclude = list(FeatureForm.Meta.exclude)
        for f in model.output_fields():
            exclude.append(f.attname)
        widgets = {}
