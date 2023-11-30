import logging
from itertools import islice

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail

from blog.models import Blog
from config import settings
from mailing.models import Mailin, AttemptsLog, Client, Message


def get_three_articles():
    articles = Blog.objects.all()  # Получить все статьи

    try:  # Получить первые три статьи, если их количество больше 3
        first_three_articles = list(islice(articles, 3))
    except IndexError:
        # Если статей меньше 3, вернуть все
        first_three_articles = articles

    return first_three_articles


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


def send_mail_save_log(
        message: Message,
        email_host,  # почта отправителя
        recipient_list,  # почты получателей в списке
        now  # время отправки
        ):
    """
    Отправляет сообщения и пишет лог (создает экземпляр AttemptsLog)
    """
    try:
        answer = send_mail(subject=message.name, message=message.text, from_email=email_host, recipient_list=recipient_list)
    except Exception as e:
        logging.error(f"Error sending email: {e}")
    else:
        if answer:
            AttemptsLog.objects.create(last_time=now, status=True, comment='Отправлено', message=message)
        else:
            AttemptsLog.objects.create(last_time=now, status=False, comment='Не отправлено', message=message)



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
            messages = mailing.message.all()
            recipient_list = get_client_emails_list(mailing)

            for message in messages:
                try:
                    # у каждого сообщения достает последний лог отправки, чтобы проверить не пришло ши время отправить
                    latest_attempts_log = AttemptsLog.objects.filter(message=message).latest('last_time')
                # Если нет объектов
                except ObjectDoesNotExist:
                    #  отправляет сообщения клиентам рассылки и получает ответ от почтового сервиса
                    send_mail_save_log(message.name, settings.EMAIL_HOST_USER, recipient_list, now)

                # Если объект найден
                else:
                    # с прошлой отправки прошло больше времени, чем интервал,

                    if ((now - latest_attempts_log.last_time).days >= swap_time_to_num(mailing.interval)
                            or not latest_attempts_log.status):  # или прошлое сообщение не было отправлено

                        #  отправляет сообщения клиентам рассылки и получает ответ от почтового сервиса
                        send_mail_save_log(message, settings.EMAIL_HOST_USER, recipient_list, now)

        # если время рассылки вышло
        else:
            mailing.status = 'inactive'
            mailing.save()
