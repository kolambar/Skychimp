import json
from datetime import datetime

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from mailing.models import Message, Mailin
from users.models import User


class MailinTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(email='testuser@mail.ru', verified_password=12354)
        user.set_password('pythonpass')
        user.save()
        self.user = User.objects.get(email='testuser@mail.ru')
        self.message = Message.objects.create(name='test1', text='abc', owner=user)

        start_naive_datetime = datetime.strptime('2024-12-01 01:02:00', '%Y-%m-%d %H:%M:%S')
        end_naive_datetime = datetime.strptime('2025-12-01 01:02:00', '%Y-%m-%d %H:%M:%S')

        self.start_aware_datetime = timezone.make_aware(start_naive_datetime)
        self.end_aware_datetime = timezone.make_aware(end_naive_datetime)

        mailin = Mailin.objects.create(name='test_mail_1', interval='daily', start_time=self.start_aware_datetime,
                              finish_time=self.end_aware_datetime, status='pending',
                              owner=self.user)
        mailin.message.add(self.message)
        mailin.save()

        self.client = Client()
        self.client.login(**{'email': 'testuser@mail.ru', 'password': 'pythonpass'})

    def test_mailing_list(self):
        response = self.client.get('/')
        assert response.status_code == 200

    def test_mailing_update(self):

        response = self.client.put(
            '/update_mailing/test_mail_1/',
            {
                "status": "active",
                "id_start_time": str(self.start_aware_datetime),
                "finish_time": str(self.end_aware_datetime),
                "interval": 0,
                "message": 1,

            }
        )
        print(response.content, "содержимое ответа")
        new_mailing = Mailin.objects.get(name='test_mail_1')
        print(new_mailing.status, "статус")
        assert response.status_code == 200
        assert new_mailing.status == 'active'


    def test_mailing_create(self):
        response = self.client.post('/create_mailing/', {
            'name': 'test_mail2',
            'interval': 'ежедневно',
            'start_time': self.start_aware_datetime,
            'finish_time': self.end_aware_datetime,
            'status': 'В ожидании',
            'message': [self.message.id],
            'owner': self.user.id,
            },
        )
        assert response.status_code == 200
        self.assertEqual(Mailin.objects.count(), 2)

    def test_create_mailin_with_invalid_data(self):
        # Попытка создать объект с некорректными данными (например, пропущено обязательное поле)
        response = self.client.post(reverse('mailin:create_mailing'), {
            'name': 'test_mail',
            'interval': 'daily',
            'start_time': '2023-12-01 01:01',
            'finish_time': '2023-12-01 01:02',
            'status': 'pending',
            # 'message': self.message.id,  # Отсутствует обязательное поле message
            'owner': self.user.id
        })

        self.assertEqual(response.status_code, 200)  # Ожидается возвращение на страницу формы
        self.assertEqual(Mailin.objects.count(), 1)  # Новый объект не должен быть создан
