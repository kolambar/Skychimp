from mailing.services import get_mailing
import datetime


def my_scheduled_job():
    mailings = get_mailing()
    now = datetime.now()
    for mailing in mailings:
        if mailing.start_time < now < mailing.finish_time:
            pass  # проверяет, прошло ли необходимое время с прошлой рассылки
