from os import environ

from celery import Celery
from celery.schedules import crontab

environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('django')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Запускаем триггерные рассылки.
    'triggers': {
        'task': 'apps.base.tasks.triggers.triggers',
        'schedule': crontab(minute=0)
    },

    # Запускаем присваивание новых статусов клиентам.
    'statuses': {
        'task': 'apps.base.tasks.statuses.statuses',
        'schedule': crontab(hour=0)
    },

    # Запускаем сгорание баллов.
    'start_the_burning_of_customer_points': {
        'task': 'apps.base.tasks.bonuses.start_the_burning_of_customer_points',
        'schedule': crontab(hour=0)
    },
}
