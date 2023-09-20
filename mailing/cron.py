import os

from mailing.models import Mailin, AttemptsLog
from mailing.services import get_mailing
import datetime


def my_scheduled_job():
    path = "/home/kolambar/Skychimp/hello"
    os.makedirs(path, exist_ok=True)
    print("Folder created!")


def check_mailing():
    now = datetime.now()

    mailings = Mailin.objects.filter(status='active')
    for mailing in mailings:
        if now < mailing.finish_time:
            messages = mailing.message
            for message in messages:
                latest_attempts_log = AttemptsLog.objects.filter(message=message).latest('lust_time')
                if now - latest_attempts_log.lust_time:
                    pass
