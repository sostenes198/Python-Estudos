from django.shortcuts import render #type: ignore
from django.http import HttpResponse

def index(request):
    return HttpResponse('Olá mundo')
