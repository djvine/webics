import os
import signal
import sys
import time
import threading
import ipdb
# EPICS
import epics
# django
os.environ['DJANGO_SETTINGS_MODULE'] = 'webics.settings'
import django
from django.utils import timezone
import scans.config
from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
# redis
import redis

redis_server=redis.Redis()
n_scan_listeners = 4 # Minimum should be the number of concurrent scans expected
 
class ScanListener(threading.Thread):
    def __init__(self, r, ioc_name):
        threading.Thread.__init__(self)
        self.redis = r
        self.ioc_name = ioc_name
        self.pref1d = self.ioc_name+':scan1'
        self.pref2d = self.ioc_name+':scan2'
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(ioc_name)
        self.pvs = {}

        self.connect_pvs()

    def epics_connect(self, pvname, auto_monitor=False, callback=None):
    
        if self.pvs.has_key(pvname):
            return True

        p = epics.PV(pvname, auto_monitor=auto_monitor)
        if callback:
            p.add_callback(callback)
        epics.poll()
        if p.connected:
            self.pvs[pvname] = p
            return True
        else:
            print '{:s} Not Connected'.format(pvname)
            return False
            
    def connect_pvs(self):
        then = time.time()

        pvnames = [
            self.ioc_name+':saveData_baseName',
            self.ioc_name+':saveData_scanNumber',
            self.ioc_name+':ScanDim',
            ]

        for pvname in pvnames:
            self.epics_connect(pvname)

        pvnames = ['.EXSC', '.P1PV', '.P1SP', '.P1EP', '.NPTS', '.P1RA', '.CPT']
        for pvname in pvnames:
            for pref in [self.pref1d, self.pref2d]:
                self.epics_connect(pref+pvname)
        
        for i in range(1, 71):
            self.epics_connect(self.pref1d+'.D{:02d}NV'.format(i))
            self.epics_connect(self.pref1d+'.D{:02d}CA'.format(i))
            self.epics_connect(self.pref1d+'.D{:02d}DA'.format(i))

        print '{:2.2f} seconds elapsed connecting to {:d} PVs'.format(time.time()-then, len(self.pvs) )

    def scan_monitor(self, item):

        # Runs once per scan.
        # Publish current scan data on redis channel and cache locally
        # At the conclusion of the scan store completed scan info to database

        print item['channel'], ":", item['data']['pvname']

        print '{:s} Engaged: Scan {:s}'.format(self, self.ioc_name)

        scan_dim_val = item['data']['value']
        if scan_dim_val == 1: # 1d scan w/no fluorescence detector
            if self.pvs[self.pref1d+'.EXSC'] == 1:
                scan_dim = {'val': 1, 'xfd': False}
                scan_outer_loop = pref1d
            else:
                print 'scanH ignored'
                return
        elif scan_dim_val == 2: 
            if self.pvs[pref2d+'.EXSC'] == 1: # 2d scan w/no fluorescence detector
                scan_dim = {'val': 2, 'xfd': False}
                scan_outer_loop = pref2d
            else: # 1d scan w/fluorescence detector
                scan_dim = {'val': 1, 'xfd': True}
                scan_outer_loop = pref1d
        elif scan_dim_val == 3: # 2d scan w/ fluorescence detector
            scan_dim = {'val': 2, 'xfd': True}
            scan_outer_loop = pref2d

        scan_id = self.pvs[self.ioc_name+':saveData_baseName'].get()+self.pvs[self.ioc_name+':saveData_scanNumber'].get()
        cache = {}

        cache['scan'] = {'scan_id': scan_id, 'ts': timezone.now()}
        x_dim = self.pvs[self.pref1d+'.NPTS'].get()
        y_dim = self.pvs[self.pref2d+'.NPTS'].get()
        cache['scan_hist'] = [{'dim': 0, 'requested': x_dim, 'completed': 0}]
        if scan_dim['val'] == 2:
            cache['scan_hist'].append({'dim': 1, 'requested': y_dim, 'completed': 0})
        cache['scan_dets'] = [ pref1d+':D{:02}CA'.format(i) for i in range(1, 71) if self.pvs[pref1d+'.D{:02}NV'].get()==0]
        cache['scan_metadata'] = [{'pvname': pref1d+'.P1PV', 'value': self.pvs[pref1d+'.P1PV'].get()},
                                  {'pvname': pref2d+'.P1PV', 'value': self.pvs[pref2d+'.P1PV'].get()}]

        if x_dim>1:
            p1sp, p1ep, p1cp = self.pvs[pref1d+'.P1SP'].get(), self.pvs[pref1d+'.P1EP'].get(), epics.caget(self.pvs[prefd+'P1PV'])
            pref1d_p1pa = np.concatenate((sp.arange(p1sp, p1ep, (p1ep-p1sp)/(p1np-1)), sp.array([p1ep])), axis=0)+p1cp
        else:
            pref1d_p1pa = sp.array([0])
        if y_dim>1:
            p1sp, p1ep, p1cp = self.pvs[pref2d+'.P1SP'].get(), self.pvs[pref2d+'.P1EP'].get(), epics.caget(self.pvs[pref2d+'P1PV'])
            pref2d_p1pa = np.concatenate((sp.arange(p1sp, p1ep, (p1ep-p1sp)/(p1np-1)), sp.array([p1ep])), axis=0)+p1cp
        else:
            pref2d_p1pa = sp.array([0])

        cache['scan_data'] = [{'pvname': pref1d+'.P1PA', 'row': 0, 'value': pref1d_p1pa},
                              {'pvname': pref2d+'.P1PA', 'row': 0, 'value': pref2d_p1pa}]
        for detector in cache['scan_dets']:
            cache['scan_data'].append({'pvname': detector, 'row': 0, 'value': sp.zeros((x_dim))})

        self.redis.publish(self.ioc_name, cache)
        updates = {}
        n_loops = 0L
        then = time.time()
        while self.pvs[scan_outer_loop+'.EXSC'].get()>0: # Scan ongoing
            if scan_dim['val']==1:
                row=0
            else:
                row = self.pvs[pref2d+'.CPT']
            for detector in cache['scan_dets']:
                updates[detector.split('.')[1][:3]+'_'+row] = self.pvs[detector].get()[:x_dim]

            self.redis.publish(self.ioc_name, updates)
            n_loops+=1
            if then-time.time()>60.0:
                print "Completed {:d} loops per min".format(n_loops)
                n_loops = 0
                then = time.time()

        # scan finished
        s = Scan(beamline=self.ioc_name, scan_id=scan_id, ts=timezone.now())
        s.save()
        s.history.create(dim=0, completed=self.pvs[pref1d+'.CPT'].get(), requested=x_dim)
        if scan_dim['val']==2:
            s.history.create(dim=1, completed=self.pvs[pref2d+'.CPT'].get(), requested=y_dim)
        for detector in cache['scan_dets']:
            s.detectors.create(active=detector.split('.')[1][:3])
        for entry in cache['scan_metadata']:
            s.metadata.create(pvname=entry['pvname'], value=entry['value'])
        s.data.create(pvname=pref1d+'.P1PA', row=0, value=pref1d_p1pa)
        s.data.create(pvname=pref2d+'.P1PA', row=0, value=pref2d_p1pa)
        for entry in updates.keys():
            s.data.create(pvname=entry.split('_')[0], row=int(entry.split('_')[1]), value=updates[entry])

        print '{:s} Disengaged'.format(self)
    
    def work(self, item):
        print item
        print item['channel'], ":", item['data']

    def run(self):
        for item in self.pubsub.listen():
            if item['data'] == "KILL":
                self.pubsub.unsubscribe()
                print self, "unsubscribed and finished"
                break
            else:
                self.work(item)


def epics_connect(pvname, auto_monitor=False, callback=None):
    
        p = epics.PV(pvname, auto_monitor=auto_monitor)
        if callback:
            p.add_callback(callback)
        epics.poll()
        if p.connected:
            return
        else:
            print '{:s} Not Connected'.format(pvname)
            return


def cb(pvname, value, **kwargs):
    print pvname, value
	redis_server.publish('new_scan', {'pvname': pvname, 'value': value})
    

def check_connectedness():
	# Check if pvs are connected
	# - Reconnect if possible
	pass


def signal_handler(signal, frame):
    # catch ctrl-c and exit gracefully
    
    # Add poison pills to kill processes
    for i in range(n_scan_listeners):
        queue.put((None,))

    sys.exit(0)

def mainloop():
    # Register for SIGINT before entering infinite loop
    signal.signal(signal.SIGINT, signal_handler)
    ipdb.set_trace()
    scan_listeners = {}

    for beamline in scans.config.ioc_names.keys():
        ioc_name = scans.config.ioc_names[beamline]
        epics_connect(ioc_name+':ScanDim.VAL', auto_monitor=True, callback=cb)
        scan_listeners[ioc_name] = ScanListener(redis_server, ioc_name)
        scan_listeners[ioc_name].start()

    while True:
        pass


if __name__=='__main__':
    mainloop()
