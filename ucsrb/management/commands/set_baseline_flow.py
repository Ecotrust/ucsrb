from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from ucsrb.models import FocusArea, TreatmentScenario
from dhsvm_harness.utils import runHarnessConfig

class Command(BaseCommand):
    help = 'Set Baseline Data. 1 argument - the name of the basin to reset: Entiat, Methow, Okanogan, or Wenatchee'
    def add_arguments(self, parser):
        parser.add_argument('basin',  type=str)

    def handle(self, *args, **options):
        import sys, csv
        # Check out Input
        try:
            basin_name = options['basin']
        except IndexError:
            self.stdout.write(
                '--- ERROR: You must provide the basin for which to run baseline data ---'
            )
            sys.exit()

        if not basin_name.lower() in settings.BASIN_RESET_LOOKUP.keys():
            self.stdout.write(
                '--- ERROR: Provided basin { not one of the valid options: Entiat, Methow, Okanogan, or Wenatchee'.format(basin_name)
            )
            sys.exit()

        basin_lookup = settings.BASIN_RESET_LOOKUP[basin_name.lower()]

        # Get reset_basin
        reset_basin_template = FocusArea.objects.get(unit_type='PourPointDiscrete', unit_id=basin_lookup['UNIT_ID'])
        reset_basin = FocusArea.objects.create(
            unit_type='Drawing',
            unit_id=reset_basin_template.unit_id,
            geometry=reset_basin_template.geometry
        )
        reset_basin.save()

        super_user = User.objects.filter(is_superuser=True)[0]

        reset_treatment = TreatmentScenario.objects.create(
            user=super_user,
            name='Reset {} Treatment'.format(basin_name),
            description="NOTR",
            focus_area=True,
            focus_area_input=reset_basin,
            # scenario=reset_scenario,
            prescription_treatment_selection='notr'
        )
        reset_treatment.save()

        runHarnessConfig(reset_treatment)

        reset_treatment.delete()
