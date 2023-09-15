from django import forms

from mailing.models import Client, Mailin


class MailinCreateForm(forms.ModelForm):
    clients = forms.ModelMultipleChoiceField(queryset=Client.objects.all(), required=False)

    class Meta:
        model = Mailin
        fields = ('name', 'start_time', 'finish_time', 'interval', 'clients',)


class MailinUpdateForm(forms.ModelForm):
    clients = forms.ModelMultipleChoiceField(queryset=Client.objects.all(), required=False)

    class Meta:
        model = Mailin
        fields = ('name', 'start_time', 'finish_time', 'interval', 'clients', 'message')