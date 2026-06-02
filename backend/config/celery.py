import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('georgetown_signal')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'recalculate-scores': {
        'task': 'apps.businesses.tasks.recalculate_reliability_scores',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    'weekly-newsletter': {
        'task': 'apps.newsletter.tasks.send_weekly_newsletter',
        'schedule': crontab(minute=0, hour=8, day_of_week='friday'),
    },
    'aggregate-signals': {
        'task': 'apps.signals.tasks.aggregate_daily_signals',
        'schedule': crontab(minute=0, hour=0),
    },
}

# Add questionnaire processing to the beat schedule
app.conf.beat_schedule.update({
    'process-questionnaire-responses': {
        'task': 'apps.reviews.tasks.process_questionnaire_responses',
        'schedule': crontab(minute=0),  # every hour
    },
})
