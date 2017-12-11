from ucsrb.models import *
from features.forms import FeatureForm
from scenarios.forms import ScenarioForm
class TreatmentScenarioForm(ScenarioForm):
    class Meta(FeatureForm.Meta):
        model = TreatmentScenario
        exclude = list(FeatureForm.Meta.exclude)
        for f in model.output_fields():
            exclude.append(f.attname)
