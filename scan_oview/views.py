from django.shortcuts import render

# Create your views here.
from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
import scans.config
import cPickle
import json
import pytz
from datetime import datetime, timedelta


# Create your views here.
def scan_oview(request, beamline='DJV'):

    td_year = timedelta(365)
    td_month = timedelta(30)
    td_week = timedelta(7)
    td_day = timedelta(1)

    scan_chrono = {}
    for item in Scan.objects.filter(beamline=beamline).filter(ts__gt=pytz.timezone('America/Chicago').localize(datetime.now())-timedelta(365)):
        scan_chrono[int(item.ts.strftime('%s'))] = 1

    scans = []
    points = []
    area = []

    # day
    items = Scan.objects.filter(beamline=beamline).filter(ts__gt=pytz.timezone('America/Chicago').localize(datetime.now())-td_day):
    scans.append(len(items))
    for item in items:
        if len(item.history.values)==1: #1D scan
            points.append(items.history.values()[0]['completed'])
        else: # 2D scan
            points.append()


    recent_scans = Scan.objects.filter(beamline=beamline).order_by('-ts')[:20]
    beamlines = sorted([{'beamline': bl} for bl in scans.config.ioc_names.keys()])
    context = {'title': 'Webics: {:s} Overview'.format(beamline), 'beamlines': beamlines, 'active_tab': beamline, 
                'data': json.dumps(scan_chrono), 'recent_scans': recent_scans}
    return render(request, 'scan_oview/scan_oview.html', context)