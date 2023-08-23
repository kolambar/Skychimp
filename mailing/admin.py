from django.contrib import admin

from mailing.models import Mailin, Client, Message, Attempts


# Register your models here.


@admin.register(Mailin)
class MailinAdmin(admin.ModelAdmin):
    list_display = ('name', 'mail_time', 'interval', 'status',)
    list_filter = ('status',)
    search_fields = ('name', 'mail_time', 'interval', 'slug',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email',)
    list_filter = ('mailin',)
    search_fields = ('name', 'email', 'mailin',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'mailing',)
    search_fields = ('name', 'mailin',)


@admin.register(Attempts)
class AttemptsAdmin(admin.ModelAdmin):
    list_display = ('data_time', 'status', 'comment')
    list_filter = ('status',)
    search_fields = ('data_time', 'status', 'comment',)
