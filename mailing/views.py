from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from config import settings
from users.models import User
from .forms import MailinCreateForm, MailinUpdateForm
from mailing.models import AttemptsLog, Message
from django.urls import reverse_lazy, reverse
from .models import Mailin, Client
from .services import get_three_articles


# Create your views here.


class MailinListView(LoginRequiredMixin, ListView):
    model = Mailin

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):  # Проверяет анонимный ли юзер. Если да, ничего не показывает
            return Mailin.objects.none()
        elif user.groups.filter(name='manager').exists():  # Менеджеру показывает все рассылки
            return super().get_queryset()
        return Mailin.objects.filter(owner=user)  # Для каждого обычного пользователя показывает только его рассылки


class MailinCreateView(LoginRequiredMixin, CreateView):
    model = Mailin
    success_url = reverse_lazy('mailin:mailing_list')  # Адрес для перенаправления после успешного создания

    def form_valid(self, form):
        user = self.request.user  # Получает текущего пользователя, который отправил форму
        self.object = form.save()
        self.object.owner = user  # Сохраняет автора
        self.object.save()

        return super().form_valid(form)

    def get_form_class(self):  # Предлагает только клиентов, которых создал пользователь\
        model_form = MailinCreateForm
        model_form.base_fields['clients'].limit_choices_to = {'owner': self.request.user}
        return model_form


class MailinDetailView(LoginRequiredMixin, DetailView):
    model = Mailin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailin = self.object
        clients = Client.objects.filter(mailin=mailin)  # Показывает только клиентов этой рассылки
        context['list_clients'] = clients
        return context


class MailinDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailin  # Модель
    success_url = reverse_lazy('mailin:mailing_list')


class MailinUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailin  # Модель

    # Тут нужно получить только клиентов этого пользователя
    form_class = MailinUpdateForm
    success_url = reverse_lazy('mailin:mailing_list')  # Адрес для перенаправления после успешного редактирования

    def get_form_class(self):  # Предлагает только клиентов, которых создал пользователь
        model_form = MailinUpdateForm
        # Следит за тем чтобы предложены только клиенты и сообщения созданные этим пользователем
        model_form.base_fields['clients'].limit_choices_to = {'owner': self.request.user}
        model_form.base_fields['message'].limit_choices_to = {'owner': self.request.user}

        return model_form

    def form_valid(self, form):
        # Сохраняет рассылку
        mailin = form.save()

        # Получает клиентов, связанных с этой рассылкой
        clients = form.cleaned_data['clients']

        # Проходим по всем клиентам и добавляет в поле mailin эту рассылку
        for client in clients:
            client.mailin.add(mailin)
            client.save()
        return super().form_valid(form)


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

    def get_form_class(self):
        model_form = super().get_form_class()  # Дает выбирать только сообщения созданные пользователем
        model_form.base_fields['mailin'].limit_choices_to = {'owner': self.request.user}
        return model_form

    def form_valid(self, form):  # Присваивает только что созданного клиента пользователю
        user = self.request.user
        instance = form.save(commit=False)
        instance.owner = user
        instance.save()
        form.save_m2m()  # Сохранят связи ManyToMany
        return super().form_valid(form)

    success_url = reverse_lazy('mailin:mailing_list')


class ClientListView(ListView):
    model = Client

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):  # Если не авторизирован, клиентов не показывает
            return Client.objects.none()
        return Client.objects.filter(owner=user)  # Показывает клиентов только созданных пользователем


class AttemptsLogListView(ListView):
    model = AttemptsLog


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ('name', 'text',)

    def form_valid(self, form):  # Присваивает только что созданного клиента пользователю
        user = self.request.user
        instance = form.save(commit=False)
        instance.owner = user
        instance.save()
        form.save_m2m()  # Сохранят связи ManyToMany
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
    """
    Проверяет, что этот пользователь менеджер. Если да, разрешает доступ
    """
    def test_func(self):
        return self.request.user.groups.filter(name='manager').exists()


class MailinManagerUpdateView(ManagerPassesTestMixin, UpdateView):
    """
    Страница для менеджера, на которой он может только менять статус рассылки
    """
    model = Mailin
    fields = ('status',)
    success_url = '/'


class UserListView(ManagerPassesTestMixin, ListView):
    """
    Страница для менеджера, на которой он может выбрать пользователя
    """
    model = User
    template_name = 'mailing/user_list.html'


class UserUpdateView(ManagerPassesTestMixin, UpdateView):
    """
    Страница для менеджера, на которой он может заблокировать или разблокировать пользователя
    """
    model = User
    fields = ('is_active',)
    success_url = '/user_list'
    template_name = 'mailing/user_form.html'


def home_page(request):
    """
    Домашняя страница
    """
    if settings.CACHE_ENABLED:
        key = 'first_three_articles'
        first_three_articles = cache.get(key)

        if first_three_articles is None:
            first_three_articles = get_three_articles()
            cache.set(key, first_three_articles)  # Кэширует рассылки

    else:
        first_three_articles = get_three_articles()

    context = {
        'all_mailing_num': Mailin.objects.count(),  # Количество всех рассылок
        'active_mailing_num': Mailin.objects.filter(status='active').count(),  # Количество активных рассылок
        'clients_num': Client.objects.count(),  # Количество клиентов
        'articles': first_three_articles  # Статьи из блога
    }

    return render(request, 'mailing/home_page.html', context)
