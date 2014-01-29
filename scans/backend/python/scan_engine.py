#!/usr/bin/env python
import os
import signal
import sys
import time
import threading
import ipdb
import cPickle
import numpy as np
import json
import datetime
# EPICS
import epics
# django
os.environ['DJANGO_SETTINGS_MODULE'] = 'webics.settings'
import django
import scans.config
from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
# redis
import redis

redis_server=redis.Redis(host='localhost', port=6379, db=0)
n_scan_listeners = 4 # Minimum should be the number of concurrent scans expected
 
class ScanListener(threading.Thread):
    def __init__(self, r, ioc_name):
        threading.Thread.__init__(self)
        self.redis = r
        self.ioc_name = ioc_name
        self.pref1d = self.ioc_name+':scan1'
        self.pref2d = self.ioc_name+':scan2'
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('new_scan')
        self.pvs = {}

        self.connect_pvs()

    def epics_connect(self, pvname, auto_monitor=False, callback=None):
    
        if self.pvs.has_key(pvname):
            return True

        p = epics.PV(pvname, auto_monitor=auto_monitor)
        if callback:
            p.add_callback(callback)
        self.pvs[pvname] = p
            
    def connect_pvs(self):
        then = time.time()

        pvnames = [
            self.ioc_name+':saveData_baseName',
            self.ioc_name+':saveData_scanNumber',
            self.ioc_name+':ScanDim',
            ]

        for pvname in pvnames:
            self.epics_connect(pvname)

        pvnames = ['.EXSC', '.P1PV', '.P1SP', '.P1EP', '.P1SI', '.P1PA', '.NPTS', '.P1RA', '.CPT']
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
        if type(item['data']) in [int, long]:
            return
        item['data'] = cPickle.loads(item['data'])
        print item['channel'], ":", item['data']['pvname']

        print '{:s} Engaged: Scan {:s}'.format(self, self.ioc_name)

        scan_dim_val = item['data']['value']
        if scan_dim_val == 1: # 1d scan w/no fluorescence detector
            if self.pvs[self.pref1d+'.EXSC'].get() == 1:
                scan_dim = {'val': 1, 'xfd': False}
                scan_outer_loop = self.pref1d
            else:
                print 'scanH ignored'
                return
        elif scan_dim_val == 2: 
            if self.pvs[self.pref2d+'.EXSC'].get() == 1: # 2d scan w/no fluorescence detector
                scan_dim = {'val': 2, 'xfd': False}
                scan_outer_loop = self.pref2d
            else: # 1d scan w/fluorescence detector
                scan_dim = {'val': 1, 'xfd': True}
                scan_outer_loop = self.pref1d
        elif scan_dim_val == 3: # 2d scan w/ fluorescence detector
            scan_dim = {'val': 2, 'xfd': True}
            scan_outer_loop = self.pref2d

        scan_id = self.pvs[self.ioc_name+':saveData_baseName'].get()+'{:04d}'.format(self.pvs[self.ioc_name+':saveData_scanNumber'].get()-1)
        cache = {}

        cache['scan'] = {'scan_id': scan_id, 'ts': datetime.datetime.now()}
        x_dim = self.pvs[self.pref1d+'.NPTS'].get()
        y_dim = self.pvs[self.pref2d+'.NPTS'].get()
        cache['scan_hist'] = [{'dim': 0, 'requested': x_dim, 'completed': 0}]
        if scan_dim['val'] == 2:
            cache['scan_hist'].append({'dim': 1, 'requested': y_dim, 'completed': 0})
        cache['scan_dets'] = [ self.pref1d+'.D{:02}CA'.format(i) for i in range(1, 71) if self.pvs[self.pref1d+'.D{:02}NV'.format(i)].get()==0]

        if x_dim>1:
            p1sp = self.pvs[self.pref1d+'.P1SP'].get()
            p1ep = self.pvs[self.pref1d+'.P1EP'].get()
            try:
                p1cp = np.float(epics.caget(epics.caget(self.pref1d+'.P1PV')))
            except: # scan1.P1PV is not defined
                p1cp = 0.0
            try:
                pref1d_p1pa = np.concatenate((np.arange(p1sp, p1ep, (p1ep-p1sp)/(x_dim-1)), np.array([p1ep])), axis=0)+p1cp
            except ZeroDivisionError: # if p1sp, p1ep initialise to 0
                pref1d_p1pa = np.arange(x_dim)

        else:
            pref1d_p1pa = np.array([0.0])
        if y_dim>1:
            p1sp = self.pvs[self.pref2d+'.P1SP'].get()
            p1ep = self.pvs[self.pref2d+'.P1EP'].get()
            try:
                p1cp = np.float(epics.caget(epics.caget(self.pref2d+'.P1PV')))
            except: # scan2.P1PV is not defined:
                p1cp = 0.0
            try:
                pref2d_p1pa = np.concatenate((np.arange(p1sp, p1ep, (p1ep-p1sp)/(y_dim-1)), np.array([p1ep])), axis=0)+p1cp
            except ZeroDivisionError:
                pref2d_p1pa = np.arange(y_dim)
        else:
            pref2d_p1pa = np.array([0.0])

        cache['scan_metadata'] = [{'pvname': self.pref1d+'.P1PV', 'value': self.pvs[self.pref1d+'.P1PV'].get()},
                                  {'pvname': self.pref2d+'.P1PV', 'value': self.pvs[self.pref2d+'.P1PV'].get()},
                                  {'pvname': self.pref2d+'.P1PA', 'value': pref2d_p1pa.tolist()}]
        json_cache = cache.copy()
        cache['scan_data'] = {}
        json_cache['scan_data'] = []
        for detector in cache['scan_dets']:
            cache['scan_data'][detector.split('.')[1][:3]+'_0'] = {'pvname': detector, 'row': 0, 'value': np.zeros((x_dim))}
            json_cache['scan_data'].append({
                'key': detector.split('.')[1][:3],
                'values': [ {
                    'name': detector.split('.')[1][:3],
                    'row': 0,
                    'x': x, 
                    'y': 0.0
                    } for x in pref1d_p1pa.tolist()]
                })

        json_cache['scan']['ts'] = json_cache['scan']['ts'].strftime("%a %d %b %H:%M")
        self.redis.publish(self.ioc_name, json.dumps({'new_scan': json_cache}))
        updates = {}
        n_loops = 0L
        then = time.time()
        cpt = -1

        while self.pvs[scan_outer_loop+'.EXSC'].get()>0: # Scan ongoing
            if scan_dim['val']==1:
                row=0
            else:
                row = self.pvs[self.pref2d+'.CPT'].get()
            
            new_cpt = self.pvs[self.pref1d+'.CPT'].get()
            if cpt != new_cpt:
                cpt = new_cpt
                for detector in cache['scan_dets']:
                    cache['scan_data'][detector.split('.')[1][:3]+'_{:d}'.format(row)] = {'pvname': detector, 
                                                'row': row, 'value': self.pvs[detector].get()[:x_dim]}                    

                    updates[detector.split('.')[1][:3]+'_{:d}'.format(row)] = {
                        'key': detector.split('.')[1][:3],
                        'values': [ {
                            'name': detector.split('.')[1][:3],
                            'row': row,
                            'x': pref1d_p1pa[i], 
                            'y': y
                            } for i, y in enumerate(cache['scan_data'][detector.split('.')[1][:3]+'_{:d}'.format(row)]['value'].tolist())]
                        }

                self.redis.publish(self.ioc_name, json.dumps({'update_scan': [entry for entry in updates.values()]}))

            n_loops+=1
            if then-time.time()>60.0:
                print "Completed {:d} loops per min".format(n_loops)
                n_loops = 0
                then = time.time()

        # scan finished
        s = Scan(beamline=self.ioc_name, scan_id=scan_id, ts=cache['scan']['ts'])
        s.save()
        s.history.create(dim=0, completed=self.pvs[self.pref1d+'.CPT'].get(), requested=x_dim)
        if scan_dim['val']==2:
            s.history.create(dim=1, completed=self.pvs[self.pref2d+'.CPT'].get(), requested=y_dim)
        for detector in cache['scan_dets']:
            s.detectors.create(active=detector.split('.')[1][1:3])
        for entry in cache['scan_metadata']:
            s.metadata.create(pvname=entry['pvname'], value=entry['value'])
        s.data.create(pvname=self.pref1d+'.P1PA', row=0, value=pref1d_p1pa)
        s.data.create(pvname=self.pref2d+'.P1PA', row=0, value=pref2d_p1pa)
        for val in cache['scan_data'].values():
            s.data.create(pvname=val['pvname'], row=val['row'], value=cPickle.dumps(val['value']))

        cache['scan_hist'] = [{'dim': 0, 'requested': x_dim, 'completed': self.pvs[self.pref1d+'.CPT'].get()}]
        if scan_dim['val'] == 2:
            cache['scan_hist'].append({'dim': 1, 'requested': y_dim, 'completed': self.pvs[self.pref2d+'.CPT'].get()})
        json_cache = {'scan': cache['scan'], 'scan_hist': cache['scan_hist']}
        self.redis.publish(self.ioc_name, json.dumps({'scan_completed': json_cache}))

        print '{:s} Disengaged'.format(self)

    def run(self):
        for item in self.pubsub.listen():
            if item['data'] == "KILL":
                self.pubsub.unsubscribe()
                print self, "unsubscribed and finished"
                break
            else:
                self.scan_monitor(item)


def epics_connect(pvname, auto_monitor=False, callback=None):
        #epics.ca.poll()
        p = epics.PV(pvname, auto_monitor=auto_monitor)
        if callback:
            p.add_callback(callback)
        #epics.ca.poll()
        if p.connected:
            return
        else:
            print '{:s} Not Connected'.format(pvname)
            return

def cb(pvname, value, **kwargs):
    print pvname, value
    if value > 0:
        redis_server.publish('new_scan', cPickle.dumps({'pvname': pvname, 'value': value}))

def signal_handler(signal, frame):
    # catch ctrl-c and exit gracefully
    print 'exiting'
    # Add poison pills to kill processes
    redis_server.publish('new_scan', 'KILL')
    for ioc_name in scans.config.ioc_names.values():
        redis_server.publish(ioc_name, 'KILL')
        
    sys.exit(0)

def mainloop():
    # Register for SIGINT before entering infinite loop
    signal.signal(signal.SIGINT, signal_handler)
    scan_listeners = {}

    for beamline in scans.config.ioc_names.keys():
        ioc_name = scans.config.ioc_names[beamline]
        epics_connect(ioc_name+':ScanDim.VAL', auto_monitor=True, callback=cb)
        scan_listeners[ioc_name] = ScanListener(redis_server, ioc_name)
        scan_listeners[ioc_name].start()

    while True:
        time.sleep(10.0)

if __name__=='__main__':
    mainloop()
