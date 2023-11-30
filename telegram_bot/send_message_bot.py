import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from telegram import Bot


async def send_to_tg(bot_token, chat_id, text):
    """
    Функция для отправки сообщений в телеграмме
    :param bot_token:
    :param chat_id:
    :param text:
    :return:
    """
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=text)
