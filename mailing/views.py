from django.views.generic import ListView
from django.shortcuts import render
from mailing.models import Mailin


# Create your views here.


class MailinListView(ListView):
    model = Mailin
