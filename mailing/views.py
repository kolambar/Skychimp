from itertools import islice

from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from blog.models import Blog
from users.models import User
from .forms import MailinCreateForm, MailinUpdateForm
from mailing.models import AttemptsLog, Message
from django.urls import reverse_lazy, reverse
from .models import Mailin, Client


# Create your views here.


class MailinListView(ListView):
    model = Mailin

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return Mailin.objects.none()
        elif user.groups.filter(name='manager').exists():
            return super().get_queryset()
        return Mailin.objects.filter(owner=user)


class MailinCreateView(LoginRequiredMixin, CreateView):
    model = Mailin
    form_class = MailinCreateForm
    success_url = reverse_lazy('mailin:mailing_list')  # Адрес для перенаправления после успешного создания

    def form_valid(self, form):
        user = self.request.user
        self.object = form.save()
        self.object.owner = user

        return super().form_valid(form)


class MailinDetailView(LoginRequiredMixin, DetailView):
    model = Mailin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailin = self.object
        clients = Client.objects.filter(mailin=mailin)
        context['list_clients'] = clients
        return context


class MailinDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailin  # Модель
    success_url = reverse_lazy('mailin:mailing_list')


class MailinUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailin  # Модель

    # тут нужно получить только клиентов этого пользователя
    form_class = MailinUpdateForm
    success_url = reverse_lazy('mailin:mailing_list')  # Адрес для перенаправления после успешного редактирования


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ('name', 'comment', 'email', 'mailin')

    def get_success_url(self):
        return reverse('mailin:detail_client', args=[self.kwargs.get('pk')])


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ('name', 'comment', 'email', 'mailin')

    def form_valid(self, form):  # присваивает только что созданного клиента пользователю
        user = self.request.user
        instance = form.save(commit=False)
        instance.owner = user
        instance.save()
        form.save_m2m()  # сохранят связи ManyToMany
        return super().form_valid(form)

    success_url = reverse_lazy('mailin:mailing_list')


class ClientListView(ListView):
    model = Client

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return Client.objects.none()
        return Client.objects.filter(owner=user)


class AttemptsLogListView(ListView):
    model = AttemptsLog


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ('name', 'text',)

    def form_valid(self, form):  # присваивает только что созданного клиента пользователю
        user = self.request.user
        instance = form.save(commit=False)
        instance.owner = user
        instance.save()
        form.save_m2m()  # сохранят связи ManyToMany
        return super().form_valid(form)

    success_url = reverse_lazy('mailin:mailing_list')  # Адрес для перенаправления после успешного редактирования



class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ('name', 'text',)
    success_url = reverse_lazy('mailin:mailing_list')  # Адрес для перенаправления после успешного редактирования


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message  # Модель
    success_url = reverse_lazy('mailin:mailing_list')


class ManagerPassesTestMixin(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.groups.filter(name='manager').exists()


class MailinManagerUpdateView(ManagerPassesTestMixin, UpdateView):
    model = Mailin
    fields = ('status',)
    success_url = '/'


class UserListView(ManagerPassesTestMixin, ListView):
    model = User
    template_name = 'mailing/user_list.html'


class UserUpdateView(ManagerPassesTestMixin, UpdateView):
    model = User
    fields = ('is_active',)
    success_url = '/user_list'
    template_name = 'mailing/user_form.html'


def home_page(request):

    articles = Blog.objects.all()  # Получить все статьи

    try:  # Получить первые три статьи, если их количество больше 3
        first_three_articles = list(islice(articles, 3))
    except IndexError:
        # Если статей меньше 3, вернуть все
        first_three_articles = articles

    context = {
        'active_mailing_num': Mailin.objects.filter(status='active').count(),
        'all_mailing_num': Mailin.objects.count(),
        'clients_num': Client.objects.count(),
        'articles': first_three_articles
    }

    return render(request, 'mailing/home_page.html', context)
