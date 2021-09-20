from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from ucsrb.models import FocusArea, TreatmentScenario
from dhsvm_harness.utils import runHarnessConfig
from time import sleep

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

        runHarnessConfig(None, basin=basin_name)
