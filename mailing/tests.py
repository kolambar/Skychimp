from django.test import TestCase, Client
from django.urls import reverse

from mailing.models import Message, Mailin
from users.models import User


class MailinTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(email='testuser@mail.ru', verified_password=12354)
        user.set_password('pythonpass')
        user.save()
        self.user = User.objects.get(email='testuser@mail.ru')
        self.message = Message.objects.create(name='test1', text='abc', owner=user)
        mailin = Mailin.objects.create(name='test_mail', interval='daily', start_time='2023-12-01 01:01',
                              finish_time='2024-12-01 01:02', status='pending',
                              owner=self.user)
        mailin.message.add(self.message)
        mailin.save()

        self.client = Client()
        self.client.login(**{'email': 'testuser@mail.ru', 'password': 'pythonpass'})

    def test_mailing_list(self):
        response = self.client.get('/')
        assert response.status_code == 200

    def test_mailing_update(self):
        print(self.client, " - self.client")
        response = self.client.patch('/create_mailing/1', {
            'name': 'test_mail',
            'interval': 'daily',
            'start_time': '2023-12-01 01:01',
            'finish_time': '2024-12-01 01:02',
            'status': 'pending',
            # 'message': [self.message.id],
            # 'owner': self.user.id
            }
        )
        print(Mailin.objects.all())
        new_mailing = Mailin.objects.get(name='test_mail')
        print(response.status_code)
        assert response.status_code == 200

    # def test_mailing_create(self):
    #     print(self.client, " - self.client")
    #     response = self.client.post('/create_mailing/', {
    #         'name': 'test_mail',
    #         'interval': 'daily',
    #         'start_time': '2023-12-01 01:01',
    #         'finish_time': '2024-12-01 01:02',
    #         'status': 'pending',
    #         'message': [self.message],
    #         'owner': self.user
    #         # 'message': [self.message.id],
    #         # 'owner': self.user.id
    #         }
    #     )
    #     print(Mailin.objects.all())
    #     new_mailing = Mailin.objects.get(name='test_mail')
    #
    #     assert response.status_code == 200

    # def test_create_mailin(self):
    #     response = self.client.post(reverse('mailin:create_mailing'), {
    #         'name': 'test_mail',
    #         'interval': 'daily',
    #         'start_time': '2023-12-01 01:01',
    #         'finish_time': '2023-12-01 01:02',
    #         'status': 'pending',
    #         'message': self.message.id,
    #         'owner': self.user.id
    #     })
    #
    #     self.assertEqual(response.status_code, 302)  # 302 означает успешное перенаправление
    #     self.assertEqual(Mailin.objects.count(), 1)  # Проверяем, что объект Mailin был создан
    #
    #     new_mailin = Mailin.objects.get(name='test_mail')
    #     self.assertEqual(new_mailin.name, 'test_mail')
    #     self.assertEqual(new_mailin.interval, 'daily')
    #     # Проверьте остальные поля, если необходимо
    #
    # def test_create_mailin_with_invalid_data(self):
    #     # Попытка создать объект с некорректными данными (например, пропущено обязательное поле)
    #     response = self.client.post(reverse('mailin:create_mailing'), {
    #         'name': 'test_mail',
    #         'interval': 'daily',
    #         'start_time': '2023-12-01 01:01',
    #         'finish_time': '2023-12-01 01:02',
    #         'status': 'pending',
    #         # 'message': self.message.id,  # Отсутствует обязательное поле message
    #         'owner': self.user.id
    #     })
    #
    #     self.assertEqual(response.status_code, 200)  # Ожидается возвращение на страницу формы
    #     self.assertEqual(Mailin.objects.count(), 0)  # Новый объект не должен быть создан
