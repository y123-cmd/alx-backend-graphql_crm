"""
CRM-specific Django settings wrapper.
This imports the main project settings and adds crm-specific configs
(crontab + celery + celery beat).
"""

from alx_backend_graphql.settings import *  # import base project settings

# Add apps
INSTALLED_APPS += [
    "django_crontab",
    "django_celery_beat",
]

# Crontab jobs
CRONJOBS = [
    ("*/5 * * * *", "crm.cron.log_crm_heartbeat"),
]

# Celery settings
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "generate-crm-report": {
        "task": "crm.tasks.generate_crm_report",
        "schedule": crontab(day_of_week="mon", hour=6, minute=0),
    },
}

