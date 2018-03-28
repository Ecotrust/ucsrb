from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Import climate Data. 1 argument - a CSV of climate data for each pour point for each timestep'
    def add_arguments(self, parser):
        parser.add_argument('file',  type=str)

    def handle(self, *args, **options):
        import sys, csv
        from ucsrb.models import ClimateData
        from datetime import datetime, timedelta

        arbitrary_start_year = 1990

        # Check out Input
        try:
            in_file_name = options['file']
        except IndexError:
            self.stdout.write('--- ERROR: You must provide the location of the climate data csv ---')
            sys.exit()

        field_map = {
            'ppt_id': None,
            'temp': None,
            'pcp': None,
            'albedo': None,
            'wind': None,
            'rh': None,
            'day': None,
            'date': None,
            'month': None,
            'year': None,
            'time': None,
            'hour': None
        }

        is_day_only = False
        is_date = False
        known_time = False
        import_count = 0
        error_count = 0

        with open(in_file_name) as csvfile:
            reader = csv.reader(csvfile, delimiter = ',')
            headers = []
            for idx, row in enumerate(reader):
                # Test for header row
                if idx == 0:
                    headers = row
                    # Read header indices into field_map lookup
                    for key in field_map.keys():
                        if key in headers:
                            field_map[key] = headers.index(key)
                    # Test that required fields are in place
                    if not set(['ppt_id','temp','pcp','albedo','wind','rh']).issubset(set(headers)):
                        print('CSV header must contain ppt_id, temp, pcp, albedo, wind, AND rh')
                        sys.exit()
                    # Test that we have enough data to assign a date value
                    if field_map['date'] and field_map['month'] and field_map['year']:
                        is_date = True
                    elif field_map['day']:
                        is_day_only = True
                    if not is_day_only and not is_date:
                        print('no reliable date tracking field(s) found. Please provide date, month, and year')
                        sys.exit()
                    # Test if a time value is supplied
                    if field_map['time']:
                        known_time = 'time'
                    elif field_map['hour']:
                        known_time = 'hour'
                    # If we have gotten this far, the data looks like it will be good
                    ClimateData.objects.all().delete()
                # Non-header rows
                else:
                    try:
                        dataObj = {}
                        # get datetime
                        if known_time:
                            day_period = int(row[field_map[day_period]])
                            if not [0,6,12,18].contains(day_period):
                                # day_period = (idx%4)*6
                                # Crazy issue with missing first record of the year:
                                # day_period = (((idx-header_count)%iterations_per_ppt)+missing_count)%timesteps_per_day*hrs_per_timestep
                                day_period = (((idx-1)%1459)+1)%4*6
                        else:
                            # day_period = (idx%4)*6
                            day_period = (((idx-1)%1459)+1)%4*6
                        if is_date:
                            date_time = datetime(
                                year=row[field_map['year']],
                                month=row[field_map['month']],
                                day=row[field_map['date']],
                                hour=day_period
                            )
                        # elif is_day_only:
                        else:
                            date_time = datetime(year=arbitrary_start_year,month=1,day=1,hour=day_period) + timedelta(int(row[field_map['day']]))
                        # assemble dict
                        dataObj['datetime'] = date_time
                        dataObj['ppt_id'] = int(row[field_map['ppt_id']])
                        dataObj['temp'] = int(row[field_map['temp']])
                        dataObj['pcp'] = float(row[field_map['pcp']])
                        dataObj['albedo'] = float(row[field_map['albedo']])
                        dataObj['wind'] = float(row[field_map['wind']])
                        dataObj['rh'] = float(row[field_map['rh']])

                        # save dict as object
                        newClimateRecord = ClimateData(**dataObj)
                        newClimateRecord.save()
                        import_count += 1
                        # print('added %d/%d climate records'% (import_count, idx))
                    except:
                        print("Unexpected error:", sys.exc_info()[0])
                        print("failed to import row %s" % str(idx))

        self.stdout.write('Successfully added %s climate records' % import_count)
