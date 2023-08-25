from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
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


class MailinDeleteView(DeleteView):
    model = Mailin  # Модель
    success_url = reverse_lazy('mailing:mailing_list')


class MailinUpdateView(UpdateView):
    model = Mailin  # Модель
    fields = ('name', 'mail_time', 'interval', 'status')  # Поля для редактирования
    success_url = reverse_lazy('students:list')  # Адрес для перенаправления после успешного редактирования
