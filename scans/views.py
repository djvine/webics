from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the scans index.")

def plots(request, beamline):
    return HttpResponse("You're looking at scan data from  %s." % beamline)

def images(request, beamline):
    response = "You're looking at scan images from %s."
    return HttpResponse(response % beamline)

