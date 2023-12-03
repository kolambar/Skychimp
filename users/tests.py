from django.test import TestCase
from django.urls import reverse

from users.models import User


class VerifyViewTest(TestCase):
    def setUp(self):
        # Создание пользователя
        self.user = User.objects.create(email='testuser@mail.ru', verified_password=12345, telegram_id=12345)
        self.user.set_password('pythonpass')
        self.user.save()

        # Зарегистрированный клиент
        self.client.login(**{'email': 'testuser@mail.ru', 'password': 'pythonpass'})

    def test_verify_user(self):

        # Подготавливаем данные для GET-запроса
        from_data = {'code': 12345}

        # Выполняет GET-запрос к представлению
        self.client.get(reverse('users:verify_view'), data=from_data)

        # Получает обновленный объект пользователя из базы данных
        updated_user = User.objects.get(email='testuser@mail.ru')

        # Проверяет, что верификация прошла успешно
        self.assertTrue(updated_user.verified)
