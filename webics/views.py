from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

from scans.models import Scan, ScanData

def home(request):

    beamlines = Scan.objects.values('beamline').distinct()

    context = {'title': 'Webics Home', 'beamlines': beamlines, 'active_tab': ""}
    return render(request, 'webics/home.html', context)