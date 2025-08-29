"""
CRM-specific Django settings wrapper.
This imports the main project settings and adds django-crontab.
"""

from alx_backend_graphql.settings import *  # import base project settings

INSTALLED_APPS += ["django_crontab"]

CRONJOBS = [
    ("*/5 * * * *", "crm.cron.log_crm_heartbeat"),
]
