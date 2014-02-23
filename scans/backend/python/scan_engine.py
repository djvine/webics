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
from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata, flush_transaction
# redis
import redis

redis_server=redis.Redis(host='localhost', port=6379, db=0)

class ClientListener(threading.Thread):
    # Listen for clients asking for historical data
    def __init__(self, r, ioc_name, beamline):
        threading.Thread.__init__(self)
        self.redis = r
        self.ioc_name = ioc_name
        self.beamline = beamline
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('hist_request')

    def get_historical_data(self, item):
        if type(item['data']) in [int, long]:
            return

        print 'Received hist data request'
        if len(item['data'].split(','))==2:
            beamline, client_id = item['data'].split(',')
            s = Scan.objects.filter(beamline=beamline).order_by('-ts')[0]
            scan_id = Scan.objects.filter(beamline='djv').order_by('-ts')[0].scan_id
        else:
            beamline, scan_id, client_id = item['data'].split(',')

        print beamline, scan_id, client_id
        cache = {}
        try:
            flush_transaction()
            s = Scan.objects.filter(beamline=beamline).filter(scan_id=scan_id).order_by('-ts')[0]
            cache['scan'] = {'scan_id': scan_id, 'ts': s.ts.strftime("%a %d %b %H:%M")}
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

            self.redis.publish('hist_reply', json.dumps({'data': cache, 'client_id': client_id}))
            print 'Sent hist data response'
        except:
            print 'Error: Unable to retrieve or send data'
            raise

    def run(self):
        for item in self.pubsub.listen():
            if item['data'] == "KILL":
                self.pubsub.unsubscribe()
                print self, "unsubscribed and finished"
                break
            else:
                if type(item['data']) in [int, long]:
                    continue
                else:
                    if item['data'].split(',')[0] == self.beamline:
                        self.get_historical_data(item)


class ScanListener(threading.Thread):
    def __init__(self, r, ioc_name, beamline):
        threading.Thread.__init__(self)
        self.redis = r
        self.ioc_name = ioc_name
        self.beamline = beamline
        self.pref1d = self.ioc_name+':scan1'
        self.pref2d = self.ioc_name+':scan2'
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('scan_begin')
        self.pvs = {}

        self.connect_pvs()

    def epics_connect(self, pvname, auto_monitor=True, callback=None):
    
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

        cache['scan'] = {'scan_id': scan_id, 'ts': cPickle.dumps(datetime.datetime.now())}
        x_dim = self.pvs[self.pref1d+'.NPTS'].get()
        y_dim = self.pvs[self.pref2d+'.NPTS'].get()
        cache['scan_hist'] = [{'dim': 0, 'requested': x_dim, 'completed': 0}]
        if scan_dim['val'] == 2:
            cache['scan_hist'].append({'dim': 1, 'requested': y_dim, 'completed': 0})
        cache['scan_dets'] = [ 'D{:02d}'.format(i) for i in range(1, 71) if self.pvs[self.pref1d+'.D{:02}NV'.format(i)].get()==0]

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
                                  {'pvname': self.pref2d+'.P1PV', 'value': self.pvs[self.pref2d+'.P1PV'].get()}]
        
        cache['scan_data'] = {}
        cache['scan_data']['y'] = {'name': cache['scan_metadata'][1]['value'], 'values': pref2d_p1pa.tolist() }
        cache['scan_data']['x'] = {'name': cache['scan_metadata'][0]['value'], 'values': pref1d_p1pa.tolist() }
        cache['scan_data']['0'] = []
        
        for detector in cache['scan_dets']:
            cache['scan_data']['0'].append(
                {'name': detector, 'values': np.zeros((1)).tolist()}
            )

        cache['scan']['ts_str'] = cPickle.loads(cache['scan']['ts']).strftime("%a %d %b %H:%M")
        self.redis.publish(self.beamline, json.dumps({'new_scan': cache}))
        
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
                cache['scan_data']['{:d}'.format(row)]=[]
                if cpt>0:
                    for detector in cache['scan_dets']:
                        cache['scan_data']['{:d}'.format(row)].append({
                            'name': detector, 
                            'values': self.pvs[self.pref1d+'.{:s}CA'.format(detector)].get(count=cpt, use_monitor=False).tolist()
                            })

                    self.redis.publish(self.beamline, json.dumps({'update_scan': cache}))

            n_loops+=1
            if time.time()-then>60.0:
                print "Completed {:d} loops per min".format(n_loops)
                n_loops = 0
                then = time.time()

        # Get final arrays
        new_cpt = self.pvs[self.pref1d+'.CPT'].get()
        if cpt != new_cpt:
            cpt = new_cpt
            cache['scan_data']['{:d}'.format(row)]=[]
            for detector in cache['scan_dets']:
                cache['scan_data']['{:d}'.format(row)].append({
                    'name': detector, 
                    'values': self.pvs[self.pref1d+'.{:s}CA'.format(detector)].get(count=cpt, use_monitor=False).tolist()
                    })

            self.redis.publish(self.beamline, json.dumps({'update_scan': cache}))

        # scan finished
        s = Scan(beamline=self.beamline, scan_id=scan_id, ts=cPickle.loads(cache['scan']['ts']))
        s.save()
        s.history.create(dim=0, completed=self.pvs[self.pref1d+'.CPT'].get(), requested=x_dim)
        if scan_dim['val']==2:
            s.history.create(dim=1, completed=self.pvs[self.pref2d+'.CPT'].get(), requested=y_dim)
        for detector in cache['scan_dets']:
            s.detectors.create(active=int(detector[1:]))
        for entry in cache['scan_metadata']:
            s.metadata.create(pvname=entry['pvname'], value=entry['value'])
        s.data.create(pvname='x', row=0, value=cPickle.dumps(pref1d_p1pa))
        s.data.create(pvname='y', row=0, value=cPickle.dumps(pref2d_p1pa))
        for key in cache['scan_data'].keys():
            if key in ['x', 'y']:
                s.data.create(pvname=key, row=0, value=cPickle.dumps(cache['scan_data'][key]['values']))
            else:
                for entry in cache['scan_data'][key]:
                    s.data.create(pvname=self.pref1d+'.'+entry['name']+'CA', row=key, value=cPickle.dumps(entry['values']))

        cache['scan_hist'] = [{'dim': 0, 'requested': x_dim, 'completed': self.pvs[self.pref1d+'.CPT'].get()}]
        if scan_dim['val'] == 2:
            cache['scan_hist'].append({'dim': 1, 'requested': y_dim, 'completed': self.pvs[self.pref2d+'.CPT'].get()})
        self.redis.publish(self.beamline, json.dumps({'completed_scan': cache}))

        print '{:s} Disengaged'.format(self)

    def run(self):
        for item in self.pubsub.listen():
            if item['data'] == "KILL":
                self.pubsub.unsubscribe()
                print self, "unsubscribed and finished"
                break
            else:
                if type(item['data']) in [int, long]:
                    continue
                else:
                    item['data'] = cPickle.loads(item['data'])
                    print item['data']['pvname'].split(':')[0], self.ioc_name
                    if item['data']['pvname'].split(':')[0] == self.ioc_name:
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
    if value > 0 and value<4:
        redis_server.publish('scan_begin', cPickle.dumps({'pvname': pvname, 'value': value}))

def signal_handler(signal, frame):
    # catch ctrl-c and exit gracefully
    print 'exiting'
    # Add poison pills to kill processes
    redis_server.publish('scan_begin', 'KILL')
    for ioc_name in scans.config.ioc_names.values():
        redis_server.publish(ioc_name, 'KILL')
        redis_server.publish('hist_request', 'KILL')
    sys.exit(0)

def mainloop():
    # Register for SIGINT before entering infinite loop
    signal.signal(signal.SIGINT, signal_handler)
    scan_listeners = {}
    client_listeners = {}

    for i, beamline in enumerate(scans.config.ioc_names.keys()):
        ioc_name = scans.config.ioc_names[beamline]
        epics_connect(ioc_name+':ScanDim.VAL', auto_monitor=True, callback=cb)
        scan_listeners[ioc_name] = ScanListener(redis_server, ioc_name, beamline)
        scan_listeners[ioc_name].start()
        client_listeners[ioc_name] = ClientListener(redis_server, ioc_name, beamline)
        client_listeners[ioc_name].start()

    while True:
        time.sleep(10.0)

if __name__=='__main__':
    mainloop()
