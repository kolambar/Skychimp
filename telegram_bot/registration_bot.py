import os
import sys
import logging
import django

# Эти две строки для docker compose. Чтобы при подъеме контейнеров находились настройки
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from config import settings
from users.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда начала работы с ботом. Если пользователь указал на сайте правильно ссылку на свой телеграмм,то
    после получения этой команды, бот привящет телеграмм пользователя к рассылке уведомлений о отправленных сообщениях
    :param update:
    :param context:
    :return:
    """
    user_id = update.message.from_user.id  # получает id пользователя
    t_link = "https://t.me/" + update.message.from_user.username  # получает из имени пользователя ссылку на его ТГ

    user = await sync_to_async(User.objects.filter(telegram=t_link).first)()  # ищет в бд пользователя с таким ТГ

    if user:
        user.telegram_id = user_id  # добавляет id чата в телеграмме в бд как telegram_id пользователя
        await sync_to_async(user.save)()  # сохраняет пользователю поля ID чата
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ваш телеграмм привязан к сайту")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Пользователь не зарегистрирован")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Здравствуйте! Это бот DeliveryStatus.\n"
                                                                          "Я буду сообщать Вам, "
                                                                          "когда сообщения отправлены.")


# Должно работать постоянно, чтобы пользователи могли привязывать свой телеграмм к сайту
if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()
    # Команда для бота
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.run_polling()
