from django.shortcuts import render
from django.http import HttpResponse
from database.db import ping

def welcome(request):
    ping()
    return HttpResponse("<h1>Welcome to TransitHub NYC</h1><p>MongoDB is connected.</p>")