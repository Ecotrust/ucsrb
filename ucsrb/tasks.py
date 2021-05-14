# Create your tasks here

from celery import shared_task
from django.conf import settings

from datetime import datetime

from threading import Thread

@shared_task
def runTreatment(treatment_id):
    from ucsrb.models import TreatmentScenario#, ScenarioStatus
    from dhsvm_harness.utils import runHarnessConfig

    treatment = TreatmentScenario.objects.get(pk=treatment_id)
    # status = ScenarioStatus.objects.get_or_create(
    #     scenario = treatment
    # )
    # if not status.status == 'complete':
    #     run_duration = datetime.now() - status.start_time
    #     if run_duration > settings.MAX_RUN_DURATION:
    #         status.status = 'queued'
    #         if status.task_id:
    #             old_task_id = task_id
    #             # TODO: Kill old task
    runHarnessConfig(treatment)
    # Thread(target=runHarnessConfig, args=(treatment,)).start()

@shared_task
def add(x, y):
    return x + y
