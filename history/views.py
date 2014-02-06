from django.shortcuts import render

# Create your views here.
from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
import scans.config

# Create your views here.
def history(request, beamline='DJV'):
    beamlines = sorted([{'beamline': bl} for bl in scans.config.ioc_names.keys()])
    recent_scans = Scan.objects.filter(beamline=beamline).order_by('-ts')[:20]
    dets = ['D{:02d}'.format(i) for i in range(1, 71)]
    context = {'title': 'Webics Home', 'beamlines': beamlines, 'active_tab': beamline,
    			'dets': dets, 'recent_scans': recent_scans}
    return render(request, 'history/history_test.html', context)