from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def index(request):
    reutn HttpResponse("UCSRB is up.")
