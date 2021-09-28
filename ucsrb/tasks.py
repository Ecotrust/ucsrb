# Create your tasks here
from celery import shared_task
from django.conf import settings

# from threading import Thread

@shared_task
def runTreatment(treatment_id, weather_year='baseline'):
    from ucsrb.models import TreatmentScenario
    from dhsvm_harness.utils import runHarnessConfig

    # see if job has been run/Get all jobs for TreatmentScenario
    treatment = TreatmentScenario.objects.get(pk=treatment_id)

    runHarnessConfig(treatment, basin=None, weather_year=weather_year)
    # Thread(target=runHarnessConfig, args=(treatment,)).start()
