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
import weave
# EPICS
import epics
# django
import django
from django.utils import timezone
from django.conf import settings
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
        self.pubsub.subscribe('hist_request_new_hist')


    def get_new_history(self, item):
        if type(item['data']) in [int, long]:
            return

        beamline, start_date, end_date, client_id = item['data'].split(',')
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%fZ')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S.%fZ')

        scans = Scan.objects.filter(beamline=beamline).filter(ts__lt=end_date.replace(tzinfo=timezone.utc),
                                                              ts__gt=start_date.replace(tzinfo=timezone.utc)).order_by('-ts')
        cache_data = []
        for s in scans:
            cache = {}
            cache['scan'] = {'scan_id': s.scan_id, 'ts': s.ts.strftime("%a %d %b %H:%M")}
            cache['scan_hist'] = [ {'dim': entry['dim'], 'completed': entry['completed'], 'requested':entry['requested']} for
                                entry in s.history.values()]
            cache_data.append(cache)
        self.redis.publish('hist_new_hist_reply', json.dumps({'data': cache_data, 'client_id': client_id}))

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
                    if item['channel']=='hist_request':
                        if item['data'].split(',')[0] == self.beamline:
                            self.get_historical_data(item)
                    elif item['channel'] == 'hist_request_new_hist':
                        if item['data'].split(',')[0] == self.beamline:
                            self.get_new_history(item)


class ScanListener(threading.Thread):
    def __init__(self, r, ioc_name, beamline):
        threading.Thread.__init__(self)
        self.redis = r
        self.ioc_name = ioc_name
        self.beamline = beamline
        self.pref1d = self.ioc_name+':scan1'
        self.pref2d = self.ioc_name+':scan2'
        self.fly_pref1d = self.ioc_name+':FscanH'
        self.fly_pref2d = self.ioc_name+':Fscan1'
        self.xfd_pref = scans.config.xfd_ioc_name[beamline]
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('scan_begin')
        self.pvs = {}

        self.c_code = """
        for (int i=0;i<n_pix;i++)// pix per buffer
        {
            for (int j=0;j<4;j++)// detector elements
            {
                for (int r=0;r<int(roi[j*2+1])-int(roi[j*2]);r++)// roi length
                {
                    res_list[i] += buff[512+i*8448+j*2048+int(roi[j*2])+r];
                }
            }
        }
        """
        if self.xfd_pref != '':
            self.precompile_weave()

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
            self.ioc_name+':FScanDim',
            ]

        # Fly scan related PVs
        if self.xfd_pref != '':
            pvnames.extend([
                self.xfd_pref+':PixelsPerBuffer_RBV',
                self.xfd_pref+':image1:ArrayData',
                self.xfd_pref+':image1:ArraySize0_RBV',
                self.xfd_pref+':netCDF1:NumCaptured_RBV',
                ])
            for detector in scans.config.fly_det_config[self.beamline].keys():
                if scans.config.fly_det_config[self.beamline][detector]!='normal':
                    roi = scans.config.fly_det_config[self.beamline][detector]
                    for m in range(4):
                        pvnames.extend([
                            self.xfd_pref+':mca{0:d}.{1:s}LO'.format(m+1, roi),
                            self.xfd_pref+':mca{0:d}.{1:s}HI'.format(m+1, roi)
                            ])

        for pvname in pvnames:
            self.epics_connect(pvname)

        pvnames = ['.EXSC', '.P1PV', '.P1SP', '.P1EP', '.P1SI', '.P1PA', '.NPTS', '.P1RA', '.CPT', '.P1AR']
        for pvname in pvnames:
            for pref in [self.pref1d, self.pref2d, self.fly_pref1d, self.fly_pref2d]:
                self.epics_connect(pref+pvname)

        # No need to monitor fly scan inner loop CPT
        setattr(self.pvs[self.fly_pref1d+'.CPT'], 'auto_monitor', False)

        for i in range(1, 71):
            self.epics_connect(self.pref1d+'.D{:02d}NV'.format(i))
            self.epics_connect(self.pref1d+'.D{:02d}CA'.format(i))
            self.epics_connect(self.pref1d+'.D{:02d}DA'.format(i))
            self.epics_connect(self.fly_pref1d+'.D{:02d}DA'.format(i))

        print '{:2.2f} seconds elapsed connecting to {:d} PVs'.format(time.time()-then, len(self.pvs) )

    def scan_monitor(self, item):

        # Runs once per scan.
        # Publish current scan data on redis channel and cache locally
        # At the conclusion of the scan store completed scan info to database

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
        flush_transaction()
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

    def precompile_weave(self):
        self.parse_buffer(124, [0,100]*4, np.arange(1047808), np.zeros(124))

    def parse_buffer(self, n_pix, roi, buff, res_list):
        weave.inline(self.c_code, ['n_pix','roi','buff','res_list'], extra_compile_args=['-O2'])


    def fly_scan_monitor(self, item):

        # Runs once per scan.
        # Publish current scan data on redis channel and cache locally
        # At the conclusion of the scan store completed scan info to database

        print '{:s} Engaged: Fly Scan {:s}'.format(self, self.ioc_name)


        scan_dim_val = item['data']['value']
        # Only 2D fly scans using Fscan1 and FscanH are supported.
        if scan_dim_val == 1: # 1d scan w/no fluorescence detector
            print "ERROR: 1D fly scans aren't supported"
            return
        elif scan_dim_val == 2:
            pass # Excellent - this is the only supported scan type
        elif scan_dim_val == 3: # 2d scan w/ fluorescence detector
            print "ERROR: 3D fly scans aren't supported"
            return

        scan_id = self.pvs[self.ioc_name+':saveData_baseName'].get()+'{:04d}'.format(self.pvs[self.ioc_name+':saveData_scanNumber'].get()-1)
        cache = {}

        cache['scan'] = {'scan_id': scan_id, 'ts': cPickle.dumps(datetime.datetime.now())}
        x_dim = self.pvs[self.fly_pref1d+'.NPTS'].get()
        y_dim = self.pvs[self.fly_pref2d+'.NPTS'].get()
        cache['scan_hist'] = [
                {'dim': 0, 'requested': x_dim, 'completed': 0},
                {'dim': 1, 'requested': y_dim, 'completed': 0}
                ]
        cache['scan_dets'] = scans.config.fly_det_config[self.beamline].keys()
        mca_dets = []
        xfd_dets = {}
        for detector in cache['scan_dets']:
            if scans.config.fly_det_config[self.beamline][detector] == 'normal':
                mca_dets.append(detector)
            else:
                roi = scans.config.fly_det_config[self.beamline][detector]
                xfd_dets[detector] = [
                    self.pvs[self.xfd_pref+':mca1.{0:s}LO'.format(roi)].get(),
                    self.pvs[self.xfd_pref+':mca1.{0:s}HI'.format(roi)].get(),
                    self.pvs[self.xfd_pref+':mca2.{0:s}LO'.format(roi)].get(),
                    self.pvs[self.xfd_pref+':mca2.{0:s}HI'.format(roi)].get(),
                    self.pvs[self.xfd_pref+':mca3.{0:s}LO'.format(roi)].get(),
                    self.pvs[self.xfd_pref+':mca3.{0:s}HI'.format(roi)].get(),
                    self.pvs[self.xfd_pref+':mca4.{0:s}LO'.format(roi)].get(),
                    self.pvs[self.xfd_pref+':mca4.{0:s}HI'.format(roi)].get()
                    ]

        if x_dim>1:
            p1sp = self.pvs[self.fly_pref1d+'.P1SP'].get()
            p1ep = self.pvs[self.fly_pref1d+'.P1EP'].get()
            if self.pvs[self.fly_pref1d+'.P1AR'].get()==1:# Relative Scan Mode
                try:
                    p1cp = np.float(epics.caget(epics.caget(self.fly_pref1d+'.P1PV')))
                except: # scan1.P1PV is not defined
                    p1cp = 0.0
            else: # Absolute Scan Mode
                p1cp = 0.0
            try:
                fly_pref1d_p1pa = np.concatenate((np.arange(p1sp, p1ep, (p1ep-p1sp)/(x_dim-1)), np.array([p1ep])), axis=0)+p1cp
            except ZeroDivisionError: # if p1sp, p1ep initialise to 0
                fly_pref1d_p1pa = np.arange(x_dim)

        else:
            fly_pref1d_p1pa = np.array([0.0])

        if y_dim>1:
            p1sp = self.pvs[self.fly_pref2d+'.P1SP'].get()
            p1ep = self.pvs[self.fly_pref2d+'.P1EP'].get()
            if self.pvs[self.fly_pref2d+'.P1AR'].get()==1:# Relative Scan Mode
                try:
                    p1cp = np.float(epics.caget(epics.caget(self.fly_pref2d+'.P1PV')))
                except: # scan2.P1PV is not defined:
                    p1cp = 0.0
            else: # Absolute scan mode
                p1cp = 0.0
            try:
                fly_pref2d_p1pa = np.concatenate((np.arange(p1sp, p1ep, (p1ep-p1sp)/(y_dim-1)), np.array([p1ep])), axis=0)+p1cp
            except ZeroDivisionError:
                fly_pref2d_p1pa = np.arange(y_dim)
        else:
            fly_pref2d_p1pa = np.array([0.0])

        cache['scan_metadata'] = [{'pvname': self.fly_pref1d+'.P1PV', 'value': self.pvs[self.fly_pref1d+'.P1PV'].get()},
                                  {'pvname': self.fly_pref2d+'.P1PV', 'value': self.pvs[self.fly_pref2d+'.P1PV'].get()}]

        cache['scan_data'] = {}
        cache['scan_data']['y'] = {'name': cache['scan_metadata'][1]['value'], 'values': fly_pref2d_p1pa.tolist() }
        cache['scan_data']['x'] = {'name': cache['scan_metadata'][0]['value'], 'values': fly_pref1d_p1pa.tolist() }
        cache['scan_data']['0'] = []

        for detector in cache['scan_dets']:
            cache['scan_data']['0'].append(
                {'name': detector, 'values': np.zeros((1)).tolist()}
            )

        cache['scan']['ts_str'] = cPickle.loads(cache['scan']['ts']).strftime("%a %d %b %H:%M")
        self.redis.publish(self.beamline, json.dumps({'new_scan': cache}))


        n_loops = 0L
        then = time.time()
        pix_per_buff = self.pvs[self.xfd_pref+':PixelsPerBuffer_RBV'].get()
        n_buffs = np.int(np.ceil(x_dim%pix_per_buff)) # Number of buffs per row
        i_buffs = 0
        buffs_uid = self.pvs[self.xfd_pref+':netCDF1:NumCaptured_RBV'].get() # Used to determine if there is a new buffer available
        buff_size = self.pvs[self.xfd_pref+':image1:ArraySize0_RBV'].get()
        cache_pos = {}
        while self.pvs[self.fly_pref2d+'.EXSC'].get()>0: # Scan ongoing
            row = self.pvs[self.fly_pref2d+'.CPT'].get()

            # Collection strategy
            # Determine how many buffers to be collected
            # From fly config determine ROI channels and corresponding detector number
            # During row accumulate buffers and convert to pixels & spectra
            # At end of line get multi-channel scaler info
            c_buffs_uid = self.pvs[self.xfd_pref+':netCDF1:NumCaptured_RBV'].get()
            if c_buffs_uid>buffs_uid: # New buffer available
                if c_buffs_uid!=buffs_uid+1: # Missed a buffer!
                    print('Error! Missed a buffer')
                buffs_uid = c_buffs_uid
                if i_buffs==0:
                    cache['scan_data']['{:d}'.format(row)]=[]
                buff = self.pvs[self.xfd_pref+':image1:ArrayData'].get(count=buff_size, use_monitor=False)
                if i_buffs < n_buffs:
                    n_pix =pix_per_buff
                else:
                    n_pix = x_dim % pix_per_buff
                print('Reading {:d} pix from buffer {:d}/{:d} of row {:d}'.format(n_pix, i_buffs, n_buffs, row))

                for detector in xfd_dets.keys():
                    res_list = np.zeros(n_pix)
                    roi = xfd_dets[detector]
                    weave.inline(self.c_code, ['n_pix', 'roi', 'buff', 'res_list'], extra_compile_args=['-O2'])
                    if i_buffs==0:
                        cache_pos[detector] = len(cache['scan_data']['{:d}'.format(row)])
                        cache['scan_data']['{:d}'.format(row)].append({
                            'name': detector,
                            'values': res_list.tolist()
                            })
                    else:
                        cache['scan_data']['{:d}'.format(row)][cache_pos[detector]]['values'].extend(res_list.tolist())

                if i_buffs == n_buffs: # End of scan line
                    for detector in mca_dets:
                        cache['scan_data']['{:d}'.format(row)].append({
                            'name': detector,
                            'values': self.pvs[self.fly_pref1d+'.{:s}DA'.format(detector)].get(count=x_dim, use_monitor=False).tolist()
                            })

                self.redis.publish(self.beamline, json.dumps({'update_scan': cache}))
                i_buffs+=1
                if i_buffs>n_buffs:
                    i_buffs=0
                    buffs_uid = -1

            n_loops+=1
            if time.time()-then>60.0:
                print "Completed {:d} loops per min".format(n_loops)
                n_loops = 0
                then = time.time()

        # scan finished
        flush_transaction()
        s = Scan(beamline=self.beamline, scan_id=scan_id, ts=cPickle.loads(cache['scan']['ts']))
        s.save()
        s.history.create(dim=0, completed=self.pvs[self.pref1d+'.CPT'].get(), requested=x_dim)
        s.history.create(dim=1, completed=self.pvs[self.pref2d+'.CPT'].get(), requested=y_dim)
        for detector in cache['scan_dets']:
            s.detectors.create(active=int(detector[1:]))
        for entry in cache['scan_metadata']:
            s.metadata.create(pvname=entry['pvname'], value=entry['value'])
        s.data.create(pvname='x', row=0, value=cPickle.dumps(fly_pref1d_p1pa))
        s.data.create(pvname='y', row=0, value=cPickle.dumps(fly_pref2d_p1pa))
        for key in cache['scan_data'].keys():
            if key in ['x', 'y']:
                s.data.create(pvname=key, row=0, value=cPickle.dumps(cache['scan_data'][key]['values']))
            else:
                for entry in cache['scan_data'][key]:
                    s.data.create(pvname=self.fly_pref1d+'.'+entry['name']+'CA', row=key, value=cPickle.dumps(entry['values']))

        cache['scan_hist'] = [{'dim': 0, 'requested': x_dim, 'completed': self.pvs[self.fly_pref1d+'.CPT'].get()}]
        cache['scan_hist'].append({'dim': 1, 'requested': y_dim, 'completed': self.pvs[self.fly_pref2d+'.CPT'].get()})
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
                    if item['data']['pvname'].split(':')[0] == self.ioc_name:
                        if item['data']['pvname'].find('FScanDim')>-1:
                            self.fly_scan_monitor(item)
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
        # Monitor ScanDim for step scans and FScanDim for fly scans
        epics_connect(ioc_name+':ScanDim.VAL', auto_monitor=True, callback=cb)
        epics_connect(ioc_name+':FScanDim.VAL', auto_monitor=True, callback=cb)
        scan_listeners[ioc_name] = ScanListener(redis_server, ioc_name, beamline)
        scan_listeners[ioc_name].start()
        client_listeners[ioc_name] = ClientListener(redis_server, ioc_name, beamline)
        client_listeners[ioc_name].start()

    while True:
        time.sleep(10.0)

if __name__=='__main__':
    try:
        with open(settings.SITE_ROOT+'/scans/backend/python/python.pid', 'r') as f:
            pid = f.readline()
            if pid:
                os.kill(int(pid), signal.SIGTERM)
    except IOError: #File doesn't exist
        pass
    except OSError: # PID doesn't exist
        pass
    with open(settings.SITE_ROOT+'/scans/backend/python/python.pid', 'w') as f:
        f.write('{0:d}'.format(os.getpid()))

    try:
        mainloop()
    finally:
        os.remove(settings.SITE_ROOT+'/scans/backend/python/python.pid')

