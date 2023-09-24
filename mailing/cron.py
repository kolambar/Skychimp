import os

from django.utils import timezone

from mailing.services import check_pending_mailing, check_active_mailing


DJANGO_SETTINGS_MODULE='config.settings'


def my_scheduled_job():
    """
    Объединяет в себе функции для проверки рассылок, которые пора запускать,
    и тех что пора останавливать или отправлять их сообщения,
    а так же дает общее время now для этих двух функций
    """
    now = timezone.now()

    check_pending_mailing(now)
    check_active_mailing(now)
