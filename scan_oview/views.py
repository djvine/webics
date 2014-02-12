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

    days = [1,2,30,365]
    n_scans = []
    n_points = []

    all_items = Scan.objects.filter(beamline=beamline)
    for day in days:
        items = all_items.filter(ts__gt=pytz.timezone('America/Chicago').localize(datetime.now())-timedelta(day))
        n_scans.append(len(items))
        tmp_pts = 0
        for item in items:
            try:
                if len(item.history.values())==1:
                    tmp_pts+=item.history.values()[0]['completed']
                else:
                    tmp_pts+=item.history.values()[0]['completed']
                    if item.history.values()[1]['completed']>1:
                        tmp_pts+=(item.history.values()[1]['completed']-1)*item.history.values()[0]['requested']
            except IndexError:
                pass
        n_points.append(tmp_pts)
    n_scans.append(len(all_items))
    tmp_pts = 0
    for item in all_items:
        try:
            if len(item.history.values())==1:
                tmp_pts+=item.history.values()[0]['completed']
            else:
                tmp_pts+=item.history.values()[0]['completed']
                if item.history.values()[1]['completed']>1:
                    tmp_pts+=(item.history.values()[1]['completed']-1)*item.history.values()[0]['requested']
        except IndexError:
            pass
    n_points.append(tmp_pts)

    scan_chrono = {}
    for item in Scan.objects.filter(beamline=beamline).filter(ts__gt=pytz.timezone('America/Chicago').localize(datetime.now())-timedelta(365)):
        scan_chrono[int(item.ts.strftime('%s'))] = 1

    recent_scans = Scan.objects.filter(beamline=beamline).order_by('-ts')[:20]
    beamlines = sorted([{'beamline': bl} for bl in scans.config.ioc_names.keys()])
    context = {'title': 'Webics: {:s} Overview'.format(beamline), 'beamlines': beamlines, 'active_tab': beamline, 
                'data': json.dumps(scan_chrono), 'recent_scans': recent_scans, 'scans': n_scans, 'points': n_points}
    return render(request, 'scan_oview/scan_oview.html', context)