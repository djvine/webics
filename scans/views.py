from django.shortcuts import render
from django.views.generic.list import ListView
from django.utils import timezone

from scans.models import Scan, ScanData
import scans.config

class ScansListView(ListView):

    model = Scan

    def get_queryset(self, **kwargs):
        return Scan.objects.all().order_by('-ts')[:50]

    def get_context_data(self, **kwargs):
        context = super(ScansListView, self).get_context_data(**kwargs)
        context['title'] = 'Webics Recent Scan Summary'
        context['beamlines'] = [{'beamline': beamline} for beamline in scans.config.beamline_list]
        context['active_tab'] = ''
        return context

def home(request):
    beamlines = [{'beamline': beamline} for beamline in scans.config.beamline_list]
    recent_scans = Scan.objects.values('scan_id').distinct().order_by('-ts')[:50]

    context = {'title': 'Webics Home', 'beamlines': beamlines, 'active_tab': "", 'recent_scans': recent_scans}
    return render(request, 'scans/home.html', context)

def plots(request):
    beamlines = [{'beamline': beamline} for beamline in scans.config.beamline_list]
    recent_scans = Scan.objects.values('scan_id').distinct().order_by('-ts')[:50]

    context = {'title': 'Webics Home', 'beamlines': beamlines, 'active_tab': "", 'recent_scans': recent_scans}
    return render(request, 'scans/home.html', context)

def images(request):
    beamlines = [{'beamline': beamline} for beamline in scans.config.beamline_list]
    recent_scans = Scan.objects.values('scan_id').distinct().order_by('-ts')[:50]

    context = {'title': 'Webics Home', 'beamlines': beamlines, 'active_tab': "", 'recent_scans': recent_scans}
    return render(request, 'scans/home.html', context)


