from django.shortcuts import render

# Create your views here.
from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
import scans.config

# Create your views here.
def lineplots(request):
    beamlines = sorted([{'beamline': beamline} for beamline in scans.config.ioc_names.keys()])
    context = {'title': 'Webics Home', 'beamlines': beamlines, 'active_tab': 'DJV'}
    return render(request, 'lineplots/lineplots_test.html', context)