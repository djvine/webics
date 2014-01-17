from django.shortcuts import render
from django.utils import timezone

from scans.models import Scan, ScanData
import scans.config

def home(request):
    beamlines = [{'beamline': beamline} for beamline in scans.config.beamline_list]

    context = {'title': 'Webics Home', 'beamlines': beamlines, 'active_tab': ''}
    return render(request, 'webics/home.html', context)