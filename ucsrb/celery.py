import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marineplanner.settings')

app = Celery('marineplanner', backend='amqp', broker='amqp://guest@localhost//', include=['ucsrb.tasks'])

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# if __name__ == '__main__':
#     app.stsart()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
