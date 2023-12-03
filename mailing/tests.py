from datetime import datetime

import telegram
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from mailing.forms import MailinCreateForm
from mailing.models import Message, Mailin, Client, AttemptsLog
from mailing.services import check_pending_mailing, swap_time_to_num, get_client_emails_list, send_mail_save_log, \
    check_active_mailing
from users.models import User


class MailinTestCase(TestCase):
    def setUp(self):
        # Создание пользователя
        self.user = User.objects.create(email='testuser@mail.ru', verified_password=12345, telegram_id=12345)
        self.user.set_password('pythonpass')
        self.user.save()

        # Зарегистрированный клиент
        self.client.login(**{'email': 'testuser@mail.ru', 'password': 'pythonpass'})

        # Создание сообщения
        self.message = Message.objects.create(name='test1', text='abc', owner=self.user)

        # Формат времени для формы
        self.start_naive_datetime = datetime.strptime('2022-12-01 01:02:00', '%Y-%m-%d %H:%M:%S')
        self.end_naive_datetime = datetime.strptime('2025-12-01 01:02:00', '%Y-%m-%d %H:%M:%S')
        self.start_date_str = self.start_naive_datetime.strftime('%Y-%m-%d')  # Формат даты
        self.start_time_str = self.start_naive_datetime.strftime('%H:%M:%S')  # Формат времени
        self.finis_date_str = self.end_naive_datetime.strftime('%Y-%m-%d')  # Формат даты
        self.finis_time_str = self.end_naive_datetime.strftime('%H:%M:%S')  # Формат времени

        # формат времени для Django ORM
        self.start_aware_datetime = timezone.make_aware(self.start_naive_datetime)
        self.end_aware_datetime = timezone.make_aware(self.end_naive_datetime)

        # Создания рассылки
        self.mailin = Mailin.objects.create(name='test_mail_1',
                                            interval='daily',
                                            start_time=self.start_aware_datetime,
                                            finish_time=self.end_aware_datetime,
                                            status='pending',
                                            owner=self.user)
        self.mailin.message.add(self.message)
        self.mailin.save()

        # Создание клиента рассылки
        self.test_client = Client.objects.create(name='test',
                                                 email='test@gmail.com',
                                                 owner=self.user)
        self.test_client.mailin.add(self.mailin)
        self.mailin.save()

        # Получение настоящего времени
        self.now = timezone.now()

    def test_mailing_list(self):
        # Выполнение запроса на список рассылок
        response = self.client.get('/')

        # Проверка код ответа
        self.assertEqual(response.status_code, 200)

        # Получение всех рассылок из базы данных
        mailing_list_from_db = Mailin.objects.all()

        # Проверка, рассылка из базы данных присутствует на странице
        for mailing in mailing_list_from_db:
            self.assertContains(response, str(mailing))

    def test_form_save_malin(self):
        # Выполнение запроса на создание объект рассылки с корректными данными
        from_data = {
            'name': 'test_mail_2',
            'interval': 'daily',
            'start_time_0': self.start_date_str,  # Дата для start_time
            'start_time_1': self.start_time_str,  # Время для start_time
            'finish_time_0': self.finis_date_str,  # Дата для finish_time
            'finish_time_1': self.finis_time_str,  # Время для finish_time
            }
        # Создает форму, проверяет ее валидность, сохраняет новую рассылку в базу данных
        form = MailinCreateForm(data=from_data)
        self.assertTrue(form.is_valid())
        form.save()
        # Проверка, что рассылка создалась
        self.assertEqual(Mailin.objects.count(), 2)

        # Меняет имя, чтобы создать другую рассылку
        from_data['name'] = 'test_mail_3'

        # Выполнение POST-запроса к представлению
        response = self.client.post(reverse('mailin:create_mailing'), from_data, follow=True)

        # Проверка код ответа
        self.assertEqual(response.status_code, 200)

        # Проверка, что объект Mailin был создан
        self.assertTrue(Mailin.objects.filter(name='test_mail_3').exists())

        # Проверка, что у объекта Mailin владелец пользователь self.user, от которого был выполнен запрос
        self.assertEqual(Mailin.objects.get(name='test_mail_3').owner, self.user)

    def test_create_mailin_with_invalid_data(self):
        # Выполнение запроса на создание объект рассылки с некорректными данными (например, пропущено обязательное поле)
        invalid_data = {
            'name': '',
            'interval': 'daily',
            'start_time_0': self.start_date_str,  # Дата для start_time
            'start_time_1': self.start_time_str,  # Время для start_time
            'finish_time_0': self.finis_date_str,  # Дата для finish_time
            'finish_time_1': self.finis_time_str,  # Время для finish_time
            }
        form = MailinCreateForm(data=invalid_data)
        # Проверяет, что форма не является валидной
        self.assertFalse(form.is_valid())
        # Проверяет, что при попытке сохранения формы возникнет исключение
        with self.assertRaises(ValueError):
            form.save()
        self.assertEqual(Mailin.objects.count(), 1)  # Объект не был создан. Есть только 1 объект из setUp

    def test_detail_view(self):
        # Выполнение запроса на получение объект рассылки
        response = self.client.get(reverse('mailin:detail_mailing', args=['test_mail_1']))

        # Проверка код ответа
        self.assertEqual(response.status_code, 200)

    def test_detail_view_anonymous(self):
        # Выполняет запроса на получение объект рассылки анонимом
        self.client.logout()
        response = self.client.get(reverse('mailin:detail_mailing', args=['test_mail_1']))
        self.assertEqual(response.status_code, 302)  # Ожидает редирект, так как доступ без авторизации запрещен

    def test_delete_mailing(self):
        # Выполняет запроса на удаление рассылки
        response = self.client.delete(reverse('mailin:delete_mailing', args=['test_mail_1']))

        # Проверяет, что после удаления мы перенаправлены на ожидаемую страницу
        self.assertRedirects(response, reverse('mailin:mailing_list'))

        # Проверяет, что рассылка действительно удалена
        self.assertEqual(Mailin.objects.filter(name='test_mail_1').exists(), False)

    def test_delete_mailing_anonymous(self):
        # Выполняет запроса на удаление рассылки анонимом
        self.client.logout()
        # Выполняет запроса на удаление рассылки
        self.client.delete(reverse('mailin:delete_mailing', args=['test_mail_1']))

        # Проверяет, что рассылка действительно удалена
        self.assertEqual(Mailin.objects.filter(name='test_mail_1').exists(), True)

    def test_check_pending_mailing(self):
        # Проверяет, что функция проверки ожидающих рассылок работает
        self.assertEqual(Mailin.objects.filter(status='pending').exists(), True)
        check_pending_mailing(self.now)

        # Обновляем данные о рассылке из базы данных
        self.mailin.refresh_from_db()
        self.assertEqual(Mailin.objects.filter(status='pending').exists(), False)

    def test_swap_time_to_num(self):
        # Проверяет, что поле интервала верно преобразовывается в число
        self.assertEqual(swap_time_to_num('daily'), 1)
        self.assertEqual(swap_time_to_num('weekly'), 7)
        self.assertEqual(swap_time_to_num('monthly'), 30)

    def test_get_client_emails_list(self):
        # Проверяет, что функция получает адреса клиентов
        # QuerySet преобразуется в список
        result_list = list(get_client_emails_list(self.mailin))
        self.assertEqual(result_list, ['test@gmail.com'])

    def test_send_mail_save_log(self):
        # Проверяет, что функция создает логи
        # Проверяет, что логов нет
        self.assertEqual(AttemptsLog.objects.all().exists(), False)

        try:
            send_mail_save_log(self.message, 'random@gmail.com', Client.objects.all(), self.now)
            # Обработка ошибки, что у тестового пользователя не настоящий id чата телеграмма
        except telegram.error.BadRequest as e:
            if "Chat not found" not in str(e):
                raise  # Если это не ошибка "Chat not found", повторно вызывает исключение

        # Проверяем, что функция создает логи
        self.assertEqual(AttemptsLog.objects.all().exists(), True)

    def test_check_old_active_mailing(self):
        # Проверяет, что функция делает неактивными старые рассылки
        # Проверяет, что неактивных рассылок нет (inactive)
        self.assertEqual(Mailin.objects.filter(status='inactive').exists(), False)

        # Создает истекшее время для новой рассылки
        end_aware_datetime = timezone.make_aware(datetime.strptime(
            '2023-12-01 01:02:00',
            '%Y-%m-%d %H:%M:%S'
        ))
        # Создает новую рассылку
        Mailin.objects.create(
            name='test_mail_2',
            interval='daily',
            start_time=self.start_aware_datetime,
            finish_time=end_aware_datetime,
            status='active',  # должна быть активной
            owner=self.user
        )
        check_active_mailing(self.now)

        # Проверяет, что появилась неактивная рассылка (inactive)
        self.assertEqual(Mailin.objects.filter(status='inactive').exists(), True)

    def test_check_actual_active_mailing(self):
        # Проверяет, что функция проверяет логи и не отправляет сообщения, если время отправки не пришло

        # Создает лог для сообщения
        self.log = AttemptsLog.objects.create(
            last_time=self.now,  # время настоящее, чтобы функция решила не отправлять сообщение
            status=True,
            message=self.message
        )

        # Создает новую рассылку
        Mailin.objects.create(
            name='test_mail_2',
            interval='daily',
            start_time=self.start_aware_datetime,
            finish_time=self.end_aware_datetime,  # должна будущим, чтобы функция не отправила рассылку в inactive
            status='active',  # должна быть активной
            owner=self.user,
        )
        self.mailin.message.add(self.message)
        check_active_mailing(self.now)

        # Проверяет, что активная рассылка осталась
        self.assertEqual(Mailin.objects.filter(status='active').exists(), True)

        # Проверяем, что в базе данных только одна запись и новая не была создана, а значит не было отправки сообщения.
        # Также не было ошибки связанной с тем, что телеграмм бот не смог отправить сообщение по некорректному id
        self.assertEqual(AttemptsLog.objects.count(), 1)

    def test_form_save_message(self):
        # Проверяет создания сообщения
        # Подготовка данных для POST-запроса
        from_data = {
            'name': 'testmessage',
            'text': 'some text',
        }

        # Выполняет POST-запроса к представлению
        response = self.client.post(reverse('mailin:create_message'), from_data, follow=True)

        # Проверяет, что объект Message был создан
        self.assertTrue(Message.objects.filter(name='testmessage').exists())

        # Проверяет созданного объекта Message
        new_message = Message.objects.get(name='testmessage')

        # Проверяет, что owner у нового сообщения соответствует текущему пользователю
        self.assertEqual(new_message.owner, self.user)

        # Проверяет, что после успешного создания записи происходит редирект
        self.assertRedirects(response, reverse('mailin:mailing_list'))

    def test_form_save_client(self):
        # Подготовка данных для POST-запроса
        from_data = {
            'name': 'testclient',
            'comment': 'some comment',
            'email': 'testclient@example.com',
            'mailin': self.mailin.id,
        }

        # Выполняет POST-запроса к представлению
        response = self.client.post(reverse('mailin:create_client'), from_data, follow=True)

        # Проверяет, что объект Client был создан
        self.assertTrue(Client.objects.filter(name='testclient').exists())

        # Получает созданного объекта Client
        new_client = Client.objects.get(name='testclient')

        # Проверяет, что owner у нового клиента соответствует текущему пользователю
        self.assertEqual(new_client.owner, self.user)

        # Проверяет, что после успешного создания записи происходит редирект
        self.assertRedirects(response, reverse('mailin:mailing_list'))
