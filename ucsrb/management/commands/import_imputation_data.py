from django.core.management.base import BaseCommand
import sys

class Command(BaseCommand):

    help = 'Import imputation data. 2 arguments - a csv pointing pourpoint ids at nearest neighbor ids, and a csv for looking up ppt/scenario by delta FC'
    def add_arguments(self, parser):
        parser.add_argument('ppt_imputation',  type=str)
        parser.add_argument('nn_lookup',  type=str)

    def handle(self, *args, **options):
        import sys
        import csv
        from ucsrb.models import PourPoint, ScenarioNNLookup

        # Check out Input
        try:
            ppt_impute_in = options['ppt_imputation']
        except IndexError:
            self.stdout.write('--- ERROR: You must provide the csv pointing pourpoint ids at nearest neighbor ids! ---')
            sys.exit()

        try:
            nn_lookup_in = options['nn_lookup']
        except IndexError:
            # self.stdout.write('--- ERROR: You must provide the csv for looking up ppt/scenario by delta FC! ---')
            # sys.exit()
            nn_lookup_in = False
            self.stdout.write('--- NO NN_LOOKUP_GIVEN: Creating new lookups will be skipped ---')

        with open(ppt_impute_in) as csvfile:
            csvReader = csv.DictReader(csvfile)
            for row in csvReader:
                try:
                    ppt = PourPoint.objects.get(id=int(row['ppt_ID']))
                    ppt.imputed_ppt = PourPoint.objects.get(id=int(row['imputedPpt']))
                    ppt.streammap_id = int(row['strmMap_id'])
                    if 'conf' in row.keys():
                        ppt.confidence = int(row['conf'])
                    if row['wshed_name'] == 'Upper Methow':     #Methow
                        ppt.watershed_id = 'met'
                    elif row['wshed_name'] == 'Upper Entiat':   #Entiat
                        ppt.watershed_id = 'ent'
                    elif row['wshed_name'] == 'Chiwawa':        #Wenatchee
                        ppt.watershed_id = 'wen'
                    ppt.save()
                except:
                    # There's some junk data in the CSV. Just skip it when the ppt doesn't exist.
                    pass

        if nn_lookup_in:
            with open(nn_lookup_in) as csvfile:
                csvReader = csv.DictReader(csvfile)
                for row in csvReader:
                    record_dict = {
                        'ppt_id': int(row['ppt_ID']),
                        'scenario_id': int(row['scen']),
                        'treatment_target': int(row['treatment']),
                        'fc_delta': float(row['delta']),
                    }
                    record, created = ScenarioNNLookup.objects.get_or_create(**record_dict)
                    record.save()
