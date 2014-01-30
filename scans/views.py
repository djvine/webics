from django.shortcuts import render
from django.views.generic.list import ListView
from django.utils import timezone

from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
import scans.config

class ScansListView(ListView):

    model = Scan

    def get_queryset(self, **kwargs):
        return Scan.objects.all().order_by('-ts')[:50]

    def get_context_data(self, **kwargs):
        context = super(ScansListView, self).get_context_data(**kwargs)
        context['title'] = 'Webics Recent Scan Summary'
        context['beamlines'] = [{'beamline': beamline} for beamline in scans.config.ioc_names.keys()]
        context['active_tab'] = 'scans'
        return context

def home(request):
    beamlines = [{'beamline': beamline} for beamline in scans.config.ioc_names.keys()]
    recent_scans = Scan.objects.values('scan_id').distinct().order_by('-ts')[:50]

    context = {'title': 'Webics Home', 'beamlines': beamlines, 'active_tab': "scans", 'recent_scans': recent_scans}
    return render(request, 'scans/home.html', context)

def plots(request, beamline):
    beamlines = [{'beamline': station} for station in scans.config.ioc_names.keys()]
    recent_scans = Scan.objects.filter(beamline=beamline).order_by('-ts')[:20]
    scan_history = [ScanHistory.objects.select_related('Scan').filter(scan=scan) for scan in recent_scans]
    dets = ['D{:02d}'.format(i) for i in range(1, 71)]

    context = {'title': 'Webics: {:s} Plots'.format(beamline), 'beamlines': beamlines, 
               'active_tab': beamline, 'recent_scans': recent_scans,
               'scan_history': scan_history, 'dets': dets}
    return render(request, 'scans/plot.html', context)

def images(request, beamline):
    beamlines = [{'beamline': beamline} for beamline in scans.config.ioc_names.keys()]
    recent_scans = Scan.objects.values('scan_id').distinct().order_by('-ts')[:50]

    context = {'title': 'Webics Home', 'beamlines': beamlines, 'active_tab': "", 'recent_scans': recent_scans}
    return render(request, 'scans/image.html', context)


