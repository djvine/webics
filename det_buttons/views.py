from django.shortcuts import render

# Create your views here.
from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
import scans.config

# Create your views here.
def det_buttons(request):
    beamlines = sorted([{'beamline': beamline} for beamline in scans.config.ioc_names.keys()])
    dets = ['D{:02d}'.format(i) for i in range(1, 71)]
    context = {'title': 'Webics Home', 'beamlines': beamlines, 'active_tab': '2-ID-B',
    			'dets': dets}
    return render(request, 'det_buttons/det_buttons_test.html', context)