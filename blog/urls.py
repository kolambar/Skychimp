from django.views.decorators.cache import cache_page

from blog.views import BlogListView, BlogCreateView, BlogDetailView, BlogUpdateView, BlogDeleteView
from mailing.apps import MailingConfig

from django.urls import path


app_name = MailingConfig.name

urlpatterns = [
    path('blog_list/', BlogListView.as_view(), name='blog_list'),
    path('create_blog/', BlogCreateView.as_view(), name='create_blog'),
    path('blog_detail/<slug:slug>', cache_page(100)(BlogDetailView.as_view()), name='blog_view'),
    path('blog_edit/<slug:slug>', BlogUpdateView.as_view(), name='blog_edit'),
    path('blog_delete/<slug:slug>', BlogDeleteView.as_view(), name='blog_delete'),
]
