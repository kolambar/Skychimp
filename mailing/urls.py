from mailing.apps import MailingConfig
from django.urls import path
from mailing.views import MailinListView, MailinCreateView, MailinDetailView, MailinDeleteView, MailinUpdateView, \
    ClientDetailView, ClientUpdateView, ClientCreateView, ClientListView, AttemptsLogListView, MessageCreateView, \
    MessageUpdateView, MessageDeleteView, MailinManagerUpdateView, UserListView, UserUpdateView, home_page

app_name = MailingConfig.name

urlpatterns = [
    path('', MailinListView.as_view(), name='mailing_list'),  # Список всех рассылок пользователя
    path('create_mailing/', MailinCreateView.as_view(), name='create_mailing'),  # Создание рассылки
    path('detail_mailing/<slug:slug>/', MailinDetailView.as_view(), name='detail_mailing'),  # Просмотр рассылки
    path('delete_mailing/<slug:slug>/', MailinDeleteView.as_view(), name='delete_mailing'),  # Удаление рассылки
    path('update_mailing/<slug:slug>/', MailinUpdateView.as_view(), name='update_mailing'),  # Обновление рассылки

    path('detail_client/<int:pk>/', ClientDetailView.as_view(), name='detail_client'),  # Просмотр клиента
    path('update_client/<int:pk>/', ClientUpdateView.as_view(), name='update_client'),  # Изменение клиента
    path('create_client/', ClientCreateView.as_view(), name='create_client'),  # Создание клиента
    path('client_list/', ClientListView.as_view(), name='client_list'),  # Список клиентов пользователя

    path('log_list/', AttemptsLogListView.as_view(), name='log_list'),  # Лог об отправке сообщений на почту

    path('create_message/', MessageCreateView.as_view(), name='create_message'),  # Создание сообщения для рассылки
    path('update_message/<int:pk>/', MessageUpdateView.as_view(), name='update_message'),  # Изменения сообщения
    path('delete_message/<int:pk>/', MessageDeleteView.as_view(), name='delete_message'),  # Удаление сообщения

    # Обновление рассылки для менеджер
    path('manager_update_mailing/<slug:slug>/', MailinManagerUpdateView.as_view(), name='manager_update_mailing'),
    path('user_list', UserListView.as_view(), name='user_list'),  # Список пользователей для менеджер
    path('update_user/<int:pk>/', UserUpdateView.as_view(), name='update_user'),  # Изменение пользователя для менеджера

    path('home_page/', home_page, name='home_page'),  # Домашняя страница с 3 статьями из блога и статистикой
]
