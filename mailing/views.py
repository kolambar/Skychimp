from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.shortcuts import render
from mailing.models import Mailin


# Create your views here.


class MailinListView(ListView):
    model = Mailin


class MailinCreateView(CreateView):
    model = Mailin
    fields = ('name', 'mail_time', 'interval',)  # Поля для заполнения при создании
    success_url = reverse_lazy('mailing:mailing_list')  # Адрес для перенаправления после успешного создания


class MailinDetailView(DetailView):
    model = Mailin
