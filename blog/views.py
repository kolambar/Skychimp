from django.contrib.auth.models import Group
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from pytils.translit import slugify

from blog.models import Blog


# Create your views here.


class ContentManagerMixin:
    """
    Получает всех контент менеджеров и помещает их в контекст, чтобы проверить, входит ли текущий юзер в их число
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Когда приложение только ставится на сервер, группы 'сontent_manager' не существует
        try:
            content_manager_group = Group.objects.get(name='сontent_manager')
            context['сontent_managers'] = content_manager_group.user_set.all()
        except Group.DoesNotExist:
            context['сontent_managers'] = None
        return context


class ContentManagerPassMixin(UserPassesTestMixin):
    """
    Ограничивает доступ для всех кроме контент-менеджеров
    """
    def test_func(self):
        return self.request.user.groups.filter(name='сontent_manager').exists()


class BlogListView(ContentManagerMixin, ListView):
    model = Blog

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(is_published=True)  # выбирает для отображения только опубликованные статьи блога
        return queryset


class BlogDetailView(ContentManagerMixin, DetailView):
    model = Blog

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.views_number += 1  # подсчитывает просмотры поста
        self.object.save()
        return self.object


class BlogCreateView(ContentManagerPassMixin, CreateView):
    model = Blog
    fields = ('header', 'text', 'image',)
    success_url = reverse_lazy('blog:blog_list')

    def form_valid(self, form):
        if form.is_valid():
            new_mat = form.save()
            new_mat.slug = slugify(new_mat.header)  # Делает slug для поста
            new_mat.save()

        return super().form_valid(form)


class BlogUpdateView(ContentManagerPassMixin, UpdateView):
    model = Blog
    fields = ('header', 'text', 'image',)
    success_url = reverse_lazy('blog:blog_list')


class BlogDeleteView(ContentManagerPassMixin, DeleteView):
    model = Blog
    success_url = reverse_lazy('blog:blog_list')
