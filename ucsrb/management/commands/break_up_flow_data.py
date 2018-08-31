from django.core.management.base import BaseCommand
import sys

class Command(BaseCommand):

    help = 'Convert 183 basin-scenario flow data csvs into thousands of basin-scenario-streammapid flow data csvs'

    def handle(self, *args, **options):
        import os
        import sys
        import csv

        DATA_LOCATION = "/%s" % os.path.join('usr','local','apps','marineplanner-core','apps','ucsrb','ucsrb','data')

        for basinFileName in os.listdir(DATA_LOCATION):
            if ".csv" in basinFileName:
                basinPrefix = basinFileName[0:6]
                BASIN_DIR = os.path.join(DATA_LOCATION,basinPrefix)
                # Make basin dir if doesn't exist
                if not os.path.exists(BASIN_DIR):
                    os.makedirs(BASIN_DIR)
                scenario = basinFileName[6:basinFileName.index('.csv')]
                # Make basin-scenario dir if doesn't exist
                BASIN_SCENARIO_DIR = os.path.join(BASIN_DIR,scenario)
                if not os.path.exists(BASIN_SCENARIO_DIR):
                    os.makedirs(BASIN_SCENARIO_DIR)
                basinFile = os.path.realpath(os.path.join(DATA_LOCATION,basinFileName))
                # HEADERS: TIMESTAMP,MONTH,DAY,YEAR,HOUR,STREAMMAPID,A,B,C,D
                # FORMAT: 10.01.2011-00:00:00,10,01,2011,00,19,351.95,39.519,391.12,0.34472
                with open(basinFile) as csvin:
                    csvReader = csv.DictReader(csvin)
                    streamMapDict = {}
                    for row in csvReader:
                        streamMapId = str(row['STREAMMAPID'])
                        if streamMapId not in streamMapDict.keys():
                            streamMapDict[streamMapId] = []
                        streamMapDict[streamMapId].append(row)

                # Write to basin-scenario-dir
                for streamMapId in streamMapDict.keys():
                    csvOutFileName = os.path.realpath(os.path.join(BASIN_SCENARIO_DIR,"%s.csv" % streamMapId))
                    fieldnames = ['TIMESTAMP','MONTH','DAY','YEAR','HOUR','C']
                    with open(csvOutFileName,'w') as csvout:
                        writer = csv.DictWriter(csvout, fieldnames=fieldnames)
                        writer.writeheader()
                        for dictionary in streamMapDict[streamMapId]:
                            subDict = {}
                            for key in fieldnames:
                                subDict[key] = dictionary[key]
                            writer.writerow(subDict)
