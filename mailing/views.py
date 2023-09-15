from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import request
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from mailing.models import AttemptsLog, Message
from .forms import MailinCreateForm, MailinUpdateForm
from .models import Mailin, Client


# Create your views here.


class MailinListView(ListView):
    model = Mailin


class MailinCreateView(LoginRequiredMixin, CreateView):
    model = Mailin
    form_class = MailinCreateForm
    success_url = '/'  # Адрес для перенаправления после успешного создания

    def form_valid(self, form):
        user = self.request.user
        form = form.save()
        form.owner = user
        return super().form_valid(form)


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


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ('name', 'comment', 'email', 'mailin')

    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        user = self.request.user
        form = form.save()
        form.owner = user
        return super().form_valid(form)


class ClientListView(ListView):
    model = Client


class AttemptsLogListView(ListView):
    model = AttemptsLog


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ('name', 'text',)
    success_url = reverse_lazy('mailing:mailing_list')  # Адрес для перенаправления после успешного редактирования

    def form_valid(self, form):
        user = self.request.user
        form = form.save()
        form.owner = user
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    model = Message
    fields = ('name', 'text',)
    success_url = reverse_lazy('mailing:mailing_list')  # Адрес для перенаправления после успешного редактирования


class MessageDeleteView(DeleteView):
    model = Message  # Модель
    success_url = reverse_lazy('mailing:mailing_list')
