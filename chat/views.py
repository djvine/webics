from django.shortcuts import render

from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
import scans.config

# Create your views here.
def chat(request):
    beamlines = sorted([{'beamline': beamline} for beamline in scans.config.ioc_names.keys()])
    context = {'title': 'Webics Home', 'beamlines': beamlines, 'active_tab': '2-ID-B'}
    return render(request, 'chat/chat_test.html', context)