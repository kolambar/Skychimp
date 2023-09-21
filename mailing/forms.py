from django import forms
from django.contrib.admin import widgets
from mailing.models import Client, Mailin


class MailinCreateForm(forms.ModelForm):

    clients = forms.ModelMultipleChoiceField(queryset=Client.objects.all(), required=False)  # подтягивает клиентов
    start_time = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime)
    finish_time = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime)

    class Meta:
        model = Mailin
        fields = ('name', 'start_time', 'finish_time', 'interval', 'clients',)


class MailinUpdateForm(forms.ModelForm):

    clients = forms.ModelMultipleChoiceField(queryset=Client.objects.all(), required=False)  # подтягивает клиентов
    start_time = forms.DateTimeField()
    finish_time = forms.DateTimeField()

    class Meta:
        model = Mailin
        fields = ('name', 'start_time', 'finish_time', 'interval', 'clients', 'message')
