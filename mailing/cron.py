import os

from django.utils import timezone

from mailing.services import check_pending_mailing, check_active_mailing


DJANGO_SETTINGS_MODULE='config.settings'


def scheduled_job():
    path = "/home/kolambar/Skychimp/hello"
    os.makedirs(path, exist_ok=True)
    print("Folder created!")


def my_scheduled_job():
    now = timezone.now()

    check_pending_mailing(now)
    check_active_mailing(now)
