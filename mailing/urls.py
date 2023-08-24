from mailing.apps import MailingConfig
from django.urls import path
from mailing.views import MailinListView, MailinCreateView, MailinDetailView

app_name = MailingConfig.name

urlpatterns = [
    path('', MailinListView.as_view(), name='mailing_list'),
    path('create_mailing/', MailinCreateView.as_view(), name='create_mailing'),
    path('detail_mailing/<slug:slug>/', MailinDetailView.as_view(), name='detail_mailing'),
]
