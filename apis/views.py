import requests
from django.shortcuts import render
from apis.email_reader import getEmails

# Create your views here.
"""Password rest done starts here"""
def first_view(request):
    if request.method == "GET":
        return render(request, 'base.html', {})