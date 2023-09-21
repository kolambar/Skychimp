from django.core.mail import send_mail

from config import settings
from mailing.models import Mailin, AttemptsLog, Client


def get_client_emails_list(mailing):
    """
    Возвращает список с email клиентов рассылки
    """
    clients = Client.objects.filter(mailin=mailing)  # подгружает клиентов из БД
    recipient_list = []

    for client in clients:
        recipient_list.append(client.email)

    return recipient_list


def swap_time_to_num(interval):
    """
    Приводит значения интервала из рассылки в дни
    """
    options = {
        'daily': 1,
        'weekly': 7,
        'monthly': 30,
    }  # в будущем можно ввести другие интервалы и присвоить им количество дней
    return options[interval]


def check_pending_mailing(now):
    """
    Проверяет отложенные рассылки. Если время подошло, меняет Mailin.status на "active"
    """
    mailings = Mailin.objects.filter(status='pending')  # подгружает ожидающие рассылки из БД

    for mailing in mailings:
        if now > mailing.start_time:  # проверяет, не пришло ли время запускать рассылку
            mailing.status = 'active'
            mailing.save()


def check_active_mailing(now):
    """
    Проверяет активные рассылки. Если время подошло, меняет Mailin.status с "active" на "inactive".
    Если пришло время отправлять сообщение с прошлой отправки, отправляет их.
    """
    mailings = Mailin.objects.filter(status='active')  # подгружает активные рассылки из БД

    for mailing in mailings:

        if now < mailing.finish_time:  # проверяет, не пришло ли время остановить рассылку
            messages = mailing.message
            recipient_list = get_client_emails_list(mailing)

            for message in messages:
                # у каждого сообщения достает последний лог отправки, чтобы проверить не пришло ши время отправить
                latest_attempts_log = AttemptsLog.objects.filter(message=message).latest('lust_time')
                if not latest_attempts_log.exist():  # если не отправлялось ни разу
                    send_mail(message.name, message.text, settings.EMAIL_HOST, recipient_list)
                else:
                    # с прошлой отправки прошло больше времени, чем интервал
                    if (now - latest_attempts_log.lust_time).days >= swap_time_to_num(mailing.interval):
                        send_mail(message.name, message.text, settings.EMAIL_HOST, recipient_list)
        # если время рассылки вышло
        else:
            mailing.status = 'inactive'
            mailing.save()
