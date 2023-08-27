from django.contrib import admin

from mailing.models import Mailin, Client, Message, AttemptsLog


# Register your models here.


@admin.register(Mailin)
class MailinAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'finish_time', 'interval', 'message',)
    list_filter = ('status',)
    search_fields = ('name', 'start_time', 'finish_time', 'interval', 'slug', 'message',)


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
    list_display = ('lust_time', 'status', 'comment')
    list_filter = ('status',)
    search_fields = ('lust_time', 'status', 'comment',)
