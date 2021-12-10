from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from ucsrb.models import TreatmentScenario
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'clears the entire django cache'

    def handle(self, *args, **options):
        anon_user = User.objects.get(pk=settings.ANONYMOUS_USER_PK)
        now = datetime.now()
        max_age = timedelta(days=3)
        for treatment in TreatmentScenario.objects.filter(user=anon_user, date_modified__lt=now-max_age):
            for area in treatment.treatmentarea_set.all():
                area.delete()
            treatment.delete()





# 0 0 * * * /usr/local/apps/env/bin/python3 /usr/local/apps/marineplanner-core/marineplanner/manage.py delete_anonymous_treatments
