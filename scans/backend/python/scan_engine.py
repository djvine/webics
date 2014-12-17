#!/usr/bin/env python
import os
import signal
import sys
import time
import threading
import ipdb
import cpickle
import numpy as np
import json
import datetime
import weave
import Queue
# EPICS
import epics
# django
import django
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import scans.config
from scans.models import User, Experiment, Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata, flush_transaction

class ScanListener(threading.Thread):
    def __init__(self, ioc_name, beamline):
        threading.Thread.__init__(self)
        self.q = Queue.Queue()
        self.user = None
        self.experiment = None
        self.ioc_name = ioc_name
        self.beamline = beamline
        self.pref1d = self.ioc_name+':scan1'
        self.pref2d = self.ioc_name+':scan2'
        self.fly_pref1d = self.ioc_name+':FscanH'
        self.fly_pref2d = self.ioc_name+':Fscan1'
        self.xfd_pref = scans.config.xfd_ioc_name[beamline]
        self.pvs = {}

        self.update_user_and_experiment()

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


    def update_user_and_experiment(self, date=dt.datetime(2014,12,10,11,0,0)):
        experiment = Experiment.objects.filter(start_date__lte=date).filter(end_date__gte=date)
        if len(experiment)==0:
            print('Could not find User and Experiment for {:}'.format(date))
            return
        self.experiment = experiment[0]
        self.user = experiment.user


    def epics_connect(self, pvname, auto_monitor=True, callback=None):

        if pvname in self.pvs:
            return True

        p = epics.PV(pvname, auto_monitor=auto_monitor)
        if callback:
            p.add_callback(callback)
        self.pvs[pvname] = p

    def connect_pvs(self):
        then = time.time()

        pvnames = [
            self.ioc_name+':saveData_fileSystem',
            self.ioc_name+':saveData_subDir',
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
            for detector in list(scans.config.fly_det_config[self.beamline].keys()):
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

        print(('{:2.2f} seconds elapsed connecting to {:d} PVs'.format(time.time()-then, len(self.pvs) )))

    def scan_monitor(self, item):

        # Runs once per scan.
        # Store scan data to database

        if not self.user:
            print('No user selected, returning.')
        if not self.experiment:
            print('No experiment defined, returning')

        print('{:s} Engaged: Scan {:s}'.format(self, self.ioc_name))

        scan_dim_val = item['data']['value']
        if scan_dim_val == 1: # 1d scan w/no fluorescence detector
            if self.pvs[self.pref1d+'.EXSC'].get() == 1:
                scan_dim = {'val': 1, 'xfd': False}
                scan_outer_loop = self.pref1d
            else:
                print('scanH ignored')
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
        x_dim = self.pvs[self.pref1d+'.NPTS'].get()
        y_dim = self.pvs[self.pref2d+'.NPTS'].get()
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

        # Save initial data to database
        flush_transaction()
        s = self.experiment.scan.create(scan_id=scan_id, ts=datetime.datetime.now())
        s.save()
        s.history.create(dim=0, completed=0, requested=x_dim)
        if scan_dim['val']==2:
            s.history.create(dim=1, completed=0, requested=y_dim)
        for detector in cache['scan_dets']:
            s.detectors.create(active=int(detector[1:]))
        s.metadata.create(pvname=self.pref1d+'.P1PV', value=self.pvs[self.pref1d+'.P1PV'].get())
        s.metadata.create(pvname=self.pref2d+'.P1PV', value=self.pvs[self.pref2d+'.P1PV'].get())
        s.data.create(pvname='x', row=0, value=cpickle.dumps(pref1d_p1pa))
        s.data.create(pvname='y', row=0, value=cpickle.dumps(pref2d_p1pa))
        with transaction.atomic():
            for detector in cache['scan_dets']:
                s.data.create(
                        pvname=self.pref1d+'.'+detector+'CA',
                        row=0,
                        value=cpickle.dumps([0])
                        )

        n_loops = 0
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
                if cpt>0:
                    with transaction.atomic():
                        for detector in cache['scan_dets']:
                            s.data.update_or_create(
                                    pvname=self.pref1+'.'+detector+'CA',
                                    row=row,
                                    value = self.pvs[self.pref1d+'.{:s}CA'.format(detector)].get(count=cpt, use_monitor=False, timeout=0.1).tolist()
                                    )


            n_loops+=1
            if time.time()-then>10.0:
                print("Completed {:d} loops per min".format(n_loops*6))
                n_loops = 0
                then = time.time()

        # Get final arrays
        new_cpt = self.pvs[self.pref1d+'.CPT'].get()
        if cpt != new_cpt:
            cpt = new_cpt

            s.history.update(dim=0, completed=self.pvs[self.pref1d+'.CPT'].get(), requested=x_dim)
            if scan_dim['val']==2:
                s.history.update(dim=1, completed=self.pvs[self.pref2d+'.CPT'].get(), requested=y_dim)
                with transaction.atomic():
                    for detector in cache['scan_dets']:
                        s.data.update_or_create(
                                pvname=self.pref1+'.'+detector+'CA',
                                row=row,
                                value = self.pvs[self.pref1d+'.{:s}CA'.format(detector)].get(count=cpt, use_monitor=False, timeout=0.1).tolist()
                                )

        print('{:s} Disengaged'.format(self))

    def precompile_weave(self):
        self.parse_buffer(124, [0,100]*4, np.arange(1047808), np.zeros(124))

    def parse_buffer(self, n_pix, roi, buff, res_list):
        weave.inline(self.c_code, ['n_pix','roi','buff','res_list'], extra_compile_args=['-O2'])

    def fly_scan_monitor(self, item):

        # Runs once per scan.
        # Publish current scan data on redis channel and cache locally
        # At the conclusion of the scan store completed scan info to database

        print('{:s} Engaged: Fly Scan {:s}'.format(self, self.ioc_name))


        scan_dim_val = item['data']['value']
        # Only 2D fly scans using Fscan1 and FscanH are supported.
        if scan_dim_val == 1: # 1d scan w/no fluorescence detector
            print("ERROR: 1D fly scans aren't supported")
            return
        elif scan_dim_val == 2:
            pass # Excellent - this is the only supported scan type
        elif scan_dim_val == 3: # 2d scan w/ fluorescence detector
            print("ERROR: 3D fly scans aren't supported")
            return

        scan_id = self.pvs[self.ioc_name+':saveData_baseName'].get()+'{:04d}'.format(self.pvs[self.ioc_name+':saveData_scanNumber'].get()-1)
        cache = {}

        x_dim = self.pvs[self.fly_pref1d+'.NPTS'].get()
        y_dim = self.pvs[self.fly_pref2d+'.NPTS'].get()
        cache['scan_dets'] = list(scans.config.fly_det_config[self.beamline].keys())
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


        flush_transaction()
        s = self.experiment.scan.create(scan_id=scan_id, ts=datetime.datetime.now())
        s.save()
        s.history.create(dim=0, completed=0, requested=x_dim)
        s.history.create(dim=1, completed=0, requested=y_dim)
        for detector in cache['scan_dets']:
            s.detectors.create(active=int(detector[1:]))
        s.metadata.create(pvname=self.fly_pref1d+'.P1PV', value=self.pvs[self.fly_pref1d+'.P1PV'].get())
        s.metadata.create(pvname=self.fly_pref2d+'.P1PV', value=self.pvs[self.fly_pref2d+'.P1PV'].get())
        s.data.create(pvname='x', row=0, value=cpickle.dumps(fly_pref1d_p1pa))
        s.data.create(pvname='y', row=0, value=cpickle.dumps(fly_pref2d_p1pa))
        with transaction.atomic():
            for detector in cache['scan_dets']:
                s.data.create(
                        pvname=self.pref1d+'.'+detector+'CA',
                        row=0,
                        value=cpickle.dumps([0])
                        )

        n_loops = 0
        then = time.time()
        pix_per_buff = self.pvs[self.xfd_pref+':PixelsPerBuffer_RBV'].get()
        n_buffs = np.int(np.ceil(x_dim/pix_per_buff)) # Number of buffs per row
        i_buffs = 0
        buffs_uid = self.pvs[self.xfd_pref+':netCDF1:NumCaptured_RBV'].get() # Used to determine if there is a new buffer available
        buff_size = self.pvs[self.xfd_pref+':image1:ArraySize0_RBV'].get()
        cache_pos = {}
        row = 0
        while self.pvs[self.fly_pref2d+'.EXSC'].get()>0: # Scan ongoing
            # Collection strategy
            # Determine how many buffers to be collected
            # From fly config determine ROI channels and corresponding detector number
            # During row accumulate buffers and convert to pixels & spectra
            # At end of line get multi-channel scaler info
            c_buffs_uid = self.pvs[self.xfd_pref+':netCDF1:NumCaptured_RBV'].get()
            if c_buffs_uid!=buffs_uid and c_buffs_uid>0: # New buffer available
                buffs_uid = c_buffs_uid
                if i_buffs==0:
                    cache['scan_data']['{:d}'.format(row)]=[]
                buff = self.pvs[self.xfd_pref+':image1:ArrayData'].get(count=buff_size, use_monitor=False).astype(np.uint16)
                if i_buffs < n_buffs:
                    n_pix =pix_per_buff
                else:
                    n_pix = x_dim % pix_per_buff
                print(('Reading {:d} pix from buffer {:d}/{:d} with uid {:d} of row {:d}'.format(n_pix, i_buffs+1, n_buffs+1, buffs_uid, row)))

                with transaction.atomic():
                    for detector in list(xfd_dets.keys()):
                        res_list = np.zeros(n_pix)
                        roi = xfd_dets[detector]
                        weave.inline(self.c_code, ['n_pix', 'roi', 'buff', 'res_list'], extra_compile_args=['-O2'])

                        s.data.update_or_create(
                                pvname=self.fly_pref1d+'.'+detector+'CA',
                                row=row,
                                value=base64.b64encodestring(res_list.tolist())
                                )

                if i_buffs == n_buffs: # End of scan line
                    with transaction.atomic():
                        for detector in mca_dets:
                            s.data.update_or_create(
                                    pvname=self.fly_pref1d+'.'+detector+'CA',
                                    row=row,
                                    value=cPickle.dumps(self.pvs[self.fly_pref1d+'.{:s}DA'.format(detector)].get(count=x_dim, use_monitor=False).tolist())
                                    )

                i_buffs+=1
                if i_buffs>n_buffs:
                    i_buffs=0
                    # Publish after scan line complete
                    then = time.time()
                    row+=1

            n_loops+=1
            if time.time()-then>10.0:
                print("Completed {:d} loops per min".format(n_loops*6))
                n_loops = 0
                then = time.time()

        # scan finished
        s.history.update(dim=0, completed=self.pvs[self.pref1d+'.CPT'].get(), requested=x_dim)
        s.history.update(dim=1, completed=self.pvs[self.pref2d+'.CPT'].get(), requested=y_dim)

        print('{:s} Disengaged'.format(self))

    def run(self):
        while True:
            message = scan_q.get()
            if message == 'KILL':
                print('Thread {:s} exiting'.format(threading.currentThread().getName()))
                break
            else:
                ioc_name, pv = message.split(':')
                if self.ioc_name==ioc_name:
                    if pvname.startswith('ScanDim'): # Step scan
                        self.scan_monitor(message)
                    elif pvname.startswith('FscanDim'): # fly scan
                        self.fly_scan_monitor(message)
                    elif pvname.startswith('saveData'): # New save directory
                        self.update_user_and_experiment()

def epics_connect(pvname, auto_monitor=False, callback=None):
        #epics.ca.poll()
        p = epics.PV(pvname, auto_monitor=auto_monitor)
        if callback:
            p.add_callback(callback)

        while not p.connected:
            time.sleep(0.1)
        return

scan_state = {}
def cb(pvname, value, **kwargs):
    """
    Here I hack together a way to ignore scans which are currently running when this script inits.
    """
    print(pvname, value)
    if pvname in list(scan_state.keys()):
        if value > 0 and value<4:
            [scan_listener.q.put(pvname) for scan_listener in scan_listeners]

    else:
        if value == 0:
            scan_state[pvname] = value

def signal_handler(signal, frame):
    # catch ctrl-c and exit gracefully
    print('exiting')
    [scan_listener.q.put('KILL') for scan_listener in scan_listeners]
    sys.exit(0)

scan_listeners = {}

def mainloop():
    # Register for SIGINT before entering infinite loop
    signal.signal(signal.SIGINT, signal_handler)

    # For each beamline start 1 scan listener
    for i, beamline in enumerate(scans.config.ioc_names.keys()):
        ioc_name = scans.config.ioc_names[beamline]
        # Monitor ScanDim for step scans and FScanDim for fly scans
        epics_connect(ioc_name+':ScanDim.VAL', auto_monitor=True, callback=cb)
        epics_connect(ioc_name+':FScanDim.VAL', auto_monitor=True, callback=cb)
        # Monitor save data path to determine when a user/experiment has changed
        # which determines who the scan data gets associated with in the db
        epics_connect(ioc_name+':saveData_subDir.VAL', auto_monitor=True, callback=cb)
        scan_listeners[ioc_name] = ScanListener(ioc_name, beamline)
        scan_listeners[ioc_name].start()

    while True:
        time.sleep(1.0)

if __name__=='__main__':
    mainloop()
