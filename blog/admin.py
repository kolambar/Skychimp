from django.contrib import admin

from blog.models import Blog


# Register your models here.


@admin.register(Blog)
class MailinAdmin(admin.ModelAdmin):
    list_display = ('header', 'text', 'creation_date', 'is_published', 'views_number',)
    list_filter = ('is_published',)
    search_fields = ('header', 'text', 'creation_date', 'slug',)
