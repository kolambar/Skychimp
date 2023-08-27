from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.shortcuts import render
from mailing.models import Mailin, AttemptsLog, Message
from django import forms
from .models import Mailin, Client


class MailinCreateForm(forms.ModelForm):
    clients = forms.ModelMultipleChoiceField(queryset=Client.objects.all(), required=False)

    class Meta:
        model = Mailin
        fields = ('name', 'start_time', 'finish_time', 'interval', 'clients',)


class MailinUpdateForm(forms.ModelForm):
    clients = forms.ModelMultipleChoiceField(queryset=Client.objects.all(), required=False)

    class Meta:
        model = Mailin
        fields = ('name', 'start_time', 'finish_time', 'interval', 'clients',)

# Create your views here.


class MailinListView(ListView):
    model = Mailin


class MailinCreateView(CreateView):
    model = Mailin
    form_class = MailinCreateForm
    success_url = reverse_lazy('mailing:mailing_list')  # Адрес для перенаправления после успешного создания


class MailinDetailView(DetailView):
    model = Mailin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailin = self.object
        clients = Client.objects.filter(mailin=mailin)
        context['list_clients'] = clients
        return context


class MailinDeleteView(DeleteView):
    model = Mailin  # Модель
    success_url = reverse_lazy('mailing:mailing_list')


class MailinUpdateView(UpdateView):
    model = Mailin  # Модель
    form_class = MailinUpdateForm
    success_url = reverse_lazy('mailing:mailing_list')  # Адрес для перенаправления после успешного редактирования


class ClientDetailView(DetailView):
    model = Client


class ClientUpdateView(UpdateView):
    model = Client
    fields = ('name', 'comment', 'email', 'mailin')

    def get_success_url(self):
        return reverse('mailing:detail_client', args=[self.kwargs.get('pk')])


class ClientCreateView(CreateView):
    model = Client
    fields = ('name', 'comment', 'email', 'mailin')

    success_url = reverse_lazy('mailing:mailing_list')


class ClientListView(ListView):
    model = Client


class AttemptsLogListView(ListView):
    model = AttemptsLog


class MessageCreateView(CreateView):
    model = Message
    fields = ('name', 'text',)
    success_url = reverse_lazy('mailing:mailing_list')  # Адрес для перенаправления после успешного редактирования
