from django.shortcuts import render

# Create your views here.
from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
import scans.config
import cPickle
import json



# Create your views here.
def images(request, beamline='DJV'):
    recent_scans = Scan.objects.filter(beamline=beamline).order_by('-ts')[:20]
    cache = {}
    try:
        s = recent_scans[0]
        cache['scan'] = {'scan_id': s.scan_id, 'ts': s.ts.strftime("%a %d %b %H:%M")}
        cache['scan_hist'] = [ {'dim': entry['dim'], 'completed': entry['completed'], 'requested':entry['requested']} for 
                            entry in s.history.values()]
        cache['scan_dets'] = ['D{:02d}'.format(entry['active']) for entry in s.detectors.values()]
        cache['scan_metadata'] = [{'pvname':entry['pvname'], 'value':entry['value']} for entry in s.metadata.values()]
        cache['scan_data'] = {}
        for entry in s.data.values():
            if entry['pvname']=='x':
                cache['scan_data']['x'] = {'name': 'x','values': cPickle.loads(str(entry['value']))}
            elif entry['pvname']=='y':
                cache['scan_data']['y'] = {'name': 'y','values': cPickle.loads(str(entry['value']))}
            else:
                try:
                    cache['scan_data'][entry['row']]
                except:
                    cache['scan_data'][entry['row']] = []
                cache['scan_data'][entry['row']].append({'name': entry['pvname'].split('.')[1][:3], 
                                                         'values': cPickle.loads(str(entry['value']))})
    except:
        print 'Error: Unable to retrieve data'

    beamlines = sorted([{'beamline': bl} for bl in scans.config.ioc_names.keys()])
    dets = dets = ['D{:02d}'.format(i) for i in range(1, 71)]
    context = {'title': 'Webics: {:s} Images'.format(beamline), 'beamlines': beamlines, 'active_tab': beamline, 
                'data': json.dumps(cache), 'dets': dets, 'recent_scans': recent_scans}
    return render(request, 'images/images.html', context)