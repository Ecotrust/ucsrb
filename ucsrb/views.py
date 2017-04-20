from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader

def index(request):
    template = loader.get_template('index.html')
    context = {
        'title': 'UCSRB FSTAT',
        'self': {
            'title': 'UCSRB Snowpack Treatment'
        }
    }
    return HttpResponse(template.render(context, request))
