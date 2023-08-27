from mailing.apps import MailingConfig
from django.urls import path
from mailing.views import MailinListView, MailinCreateView, MailinDetailView, MailinDeleteView, MailinUpdateView, \
    ClientDetailView, ClientUpdateView, ClientCreateView, ClientListView, AttemptsLogListView, MessageCreateView

app_name = MailingConfig.name

urlpatterns = [
    path('', MailinListView.as_view(), name='mailing_list'),
    path('create_mailing/', MailinCreateView.as_view(), name='create_mailing'),
    path('detail_mailing/<slug:slug>/', MailinDetailView.as_view(), name='detail_mailing'),
    path('delete_mailing/<slug:slug>/', MailinDeleteView.as_view(), name='delete_mailing'),
    path('update_mailing/<slug:slug>/', MailinUpdateView.as_view(), name='update_mailing'),
    path('detail_client/<int:pk>/', ClientDetailView.as_view(), name='detail_client'),
    path('update_client/<int:pk>/', ClientUpdateView.as_view(), name='update_client'),
    path('create_client/', ClientCreateView.as_view(), name='create_client'),
    path('client_list/', ClientListView.as_view(), name='client_list'),
    path('log_list/', AttemptsLogListView.as_view(), name='log_list'),
    path('create_message/', MessageCreateView.as_view(), name='create_message'),

]
