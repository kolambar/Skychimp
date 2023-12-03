from datetime import date

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from blog.models import Blog
from mailing.services import get_three_articles
from users.models import User


class BlogTestCase(TestCase):
    def setUp(self):
        # Создание пользователя
        self.user = User.objects.create(email='testuser@mail.ru', verified_password=12345, telegram_id=12345)
        self.user.set_password('pythonpass')
        self.user.save()

        # Зарегистрированный клиент
        self.client.login(**{'email': 'testuser@mail.ru', 'password': 'pythonpass'})

        # Создание блога
        self.test_blog = Blog.objects.create(
            header='test_header_1',
            slug='test_header_1',
            text='some text',
            creation_date=date(2022, 12, 1),
        )

    def test_get_three_articles(self):
        # Проверяет, что функция возвращает блог
        self.assertEqual(get_three_articles(), [self.test_blog])

        blog_data = [
            {'header': 'test_header_2', 'text': 'some text', 'creation_date': date(2022, 12, 1)},
            {'header': 'test_header_3', 'text': 'some text', 'creation_date': date(2022, 12, 1)},
        ]

        test_blogs = Blog.objects.bulk_create([Blog(**data) for data in blog_data])

        # Проверяет, что функция возвращает 3 блога
        self.assertEqual(get_three_articles(), [self.test_blog, *test_blogs])

        # Проверяет, что функция возвращает только 3 блога
        Blog.objects.create(
            header='test_header_4',
            text='some text',
            creation_date=date(2022, 12, 1),
        )
        self.assertEqual(get_three_articles(), [self.test_blog, *test_blogs])

    def test_blog_list(self):
        # Выполнение запроса на список постов
        response = self.client.get(reverse('blog:blog_list'))

        self.assertEqual(response.status_code, 200)
        # Проверка, пост из базы данных присутствует на странице
        self.assertContains(response, 'test_header_1')  # название блога есть на странице

    def test_blog_detail(self):
        # Выполнение запроса на пост
        response = self.client.get(reverse('blog:blog_view', kwargs={'slug': 'test_header_1'}))

        self.assertEqual(response.status_code, 200)
        # Проверка, пост из базы данных присутствует на странице
        self.assertContains(response, 'test_header_1')  # название блога есть на странице

    def test_form_save_blog(self):
        # Выполнение запроса на создание объект блога с корректными данными
        # Создание группы content_manager
        content_manager_group = Group.objects.create(name='content_manager')

        # Добавление пользователя в группу
        self.user.groups.add(content_manager_group)
        self.user.save()

        # Авторизация пользователя
        self.client.force_login(self.user)

        from_data = {
            'header': 'testheader2',
            'text': 'some text',
            'creation_date': date(2022, 12, 1)
        }

        # Выполнение POST-запроса к представлению
        response = self.client.post(reverse('blog:create_blog'), from_data, follow=True)

        # Проверка, что объект Blog был создан
        self.assertTrue(Blog.objects.filter(header='testheader2').exists())

        # Получение созданного объекта Blog
        new_blog = Blog.objects.get(header='testheader2')

        # Проверка, что slug был создан и соответствует ожидаемому значению
        self.assertEqual(new_blog.slug, 'testheader2')

        # Проверка, что после успешного создания записи происходит редирект
        self.assertRedirects(response, reverse('blog:blog_list'))
