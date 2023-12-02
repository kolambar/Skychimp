import json
from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from mailing.forms import MailinCreateForm
from mailing.models import Message, Mailin, Client
from users.models import User


class MailinTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(email='testuser@mail.ru', verified_password=12345)
        user.set_password('pythonpass')
        user.save()

        # Зарегистрированный клиент
        self.client.login(**{'email': 'testuser@mail.ru', 'password': 'pythonpass'})

        self.user = User.objects.get(email='testuser@mail.ru')
        self.message = Message.objects.create(name='test1', text='abc', owner=user)

        # Формат времени для формы
        self.start_naive_datetime = datetime.strptime('2024-12-01 01:02:00', '%Y-%m-%d %H:%M:%S')
        self.end_naive_datetime = datetime.strptime('2025-12-01 01:02:00', '%Y-%m-%d %H:%M:%S')
        self.start_date_str = self.start_naive_datetime.strftime('%Y-%m-%d')  # Формат даты
        self.start_time_str = self.start_naive_datetime.strftime('%H:%M:%S')  # Формат времени
        self.finis_date_str = self.end_naive_datetime.strftime('%Y-%m-%d')  # Формат даты
        self.finis_time_str = self.end_naive_datetime.strftime('%H:%M:%S')  # Формат времени

        # формат времени для Django ORM
        start_aware_datetime = timezone.make_aware(self.start_naive_datetime)
        end_aware_datetime = timezone.make_aware(self.end_naive_datetime)

        self.mailin = Mailin.objects.create(name='test_mail_1',
                                            interval='daily',
                                            start_time=start_aware_datetime,
                                            finish_time=end_aware_datetime,
                                            status='pending',
                                            owner=self.user)
        self.mailin.message.add(self.message)
        self.mailin.save()

        self.test_client = Client.objects.create(name='test',
                                                 email='test@gmail.com',
                                                 owner=self.user)
        self.test_client.mailin.add(self.mailin)
        self.mailin.save()

    def test_mailing_list(self):
        response = self.client.get('/')
        assert response.status_code == 200

    def test_form_save_malin(self):
        # Попытка создать объект рассылки с корректными данными
        from_data = {
            'name': 'test_mail_2',
            'interval': 'daily',
            'start_time_0': self.start_date_str,  # Дата для start_time
            'start_time_1': self.start_time_str,  # Время для start_time
            'finish_time_0': self.finis_date_str,  # Дата для finish_time
            'finish_time_1': self.finis_time_str,  # Время для finish_time
            }
        form = MailinCreateForm(data=from_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Mailin.objects.count(), 2)

    def test_create_mailin_with_invalid_data(self):
        # Попытка создать объект рассылки с некорректными данными (например, пропущено обязательное поле)
        invalid_data = {
            'name': '',
            'interval': 'daily',
            'start_time_0': self.start_date_str,  # Дата для start_time
            'start_time_1': self.start_time_str,  # Время для start_time
            'finish_time_0': self.finis_date_str,  # Дата для finish_time
            'finish_time_1': self.finis_time_str,  # Время для finish_time
            }
        form = MailinCreateForm(data=invalid_data)
        self.assertFalse(form.is_valid())  # Проверяет, что форма не является валидной
        with self.assertRaises(ValueError):  # Проверяет, что при попытке сохранения формы возникнет исключение
            form.save()
        self.assertEqual(Mailin.objects.count(), 1)  # Объект не был создан. Есть только 1 объект из setUp

    def test_detail_view(self):
        # Попытка получить объект рассылки
        response = self.client.get(reverse('mailin:detail_mailing', args=['test_mail_1']))
        assert response.status_code == 200

    def test_detail_view_anonymous(self):
        # Попытка получить объект рассылки анонимом
        self.client.logout()
        response = self.client.get(reverse('mailin:detail_mailing', args=['test_mail_1']))
        self.assertEqual(response.status_code, 302)  # Ожидает редирект, так как доступ без авторизации запрещен

    def test_delete_mailing(self):
        # Выполнение запроса на удаление рассылки
        response = self.client.delete(reverse('mailin:delete_mailing', args=['test_mail_1']))

        # проверка, что после удаления мы перенаправлены на ожидаемую страницу
        self.assertRedirects(response, reverse('mailin:mailing_list'))

        # проверка, что рассылка действительно удалена
        self.assertEqual(Mailin.objects.filter(name='test_mail_1').exists(), False)

    def test_delete_mailing_anonymous(self):
        # Выполнение запроса на удаление рассылки анонимом
        self.client.logout()
        # выполнение запроса на удаление рассылки
        response = self.client.delete(reverse('mailin:delete_mailing', args=['test_mail_1']))

        # проверка, что рассылка действительно удалена
        self.assertEqual(Mailin.objects.filter(name='test_mail_1').exists(), True)
