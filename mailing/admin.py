from django.contrib import admin

from mailing.models import Mailin, Client, Message, AttemptsLog


# Register your models here.


@admin.register(Mailin)
class MailinAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'finish_time', 'interval',)
    list_filter = ('status',)
    search_fields = ('name', 'start_time', 'finish_time', 'interval', 'slug',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email',)
    list_filter = ('mailin',)
    search_fields = ('name', 'email', 'mailin',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(AttemptsLog)
class AttemptsAdmin(admin.ModelAdmin):
    list_display = ('last_time', 'status', 'comment')
    list_filter = ('status',)
    search_fields = ('last_time', 'status', 'comment',)
