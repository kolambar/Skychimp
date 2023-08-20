from django.shortcuts import render
from msilib.schema import ListView


# Create your views here.


class MailingListView(ListView):
    model = Mailing