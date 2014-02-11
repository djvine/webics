from django.shortcuts import render

# Create your views here.
from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
import scans.config
import cPickle
import json



# Create your views here.
def scan_oview(request, beamline='DJV'):

	scan_year = Scan.objects.filter(beamline=beamline)

    beamlines = sorted([{'beamline': bl} for bl in scans.config.ioc_names.keys()])
    context = {'title': 'Webics: {:s} Line Plots'.format(beamline), 'beamlines': beamlines, 'active_tab': beamline, 
                'data': json.dumps( cache), 'dets': dets, 'recent_scans': recent_scans}
    return render(request, 'lineplots/lineplots.html', context)