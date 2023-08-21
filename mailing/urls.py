from mailing.views import MailingListView
from mailing.apps import MailingConfig
from django.urls import path


app_name = MailingConfig.name

urlpatterns = [
    path('', MailingListView, name='list_mailing'),
]