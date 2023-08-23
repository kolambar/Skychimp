from mailing.apps import MailingConfig
from django.urls import path
from mailing.views import MailinListView


app_name = MailingConfig.name

urlpatterns = [
    path('', MailinListView.as_view(), name='mailing_list'),
]
