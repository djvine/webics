#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('./scans/backend/python'))
import time
import threading
import ipdb
import numpy as np
from readMDA import readMDA
import datetime
import glob
import h5py
# django
import django
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
import scans.config
from scans.models import UserProfile, Experiment, Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata, flush_transaction
import schedule

"""
Import Scan Data Into Database

Strategy
-------
for each user directory:
    1: Query schedule system to determine who was user based on mda timestamp
    2: Create user and experiment
    3: For each mda file:
    4:  Create a scan entry for the raw data
    5:  Create a scan entry for the analysed data
"""
debug = True
class Importer():

    def __init__(self, directory):
        self.directory = directory
        self.beamline = '2-ID-E'

    def run(self):
        ipdb.set_trace()
        if not os.path.exists(os.path.join(self.directory, 'mda')):
            print('Could not find mda directory. Exiting')
            sys.exit(1)

        mda_filenames = glob.glob(os.path.join(self.directory, 'mda/*.mda'))
        print('Found {:d} mda files.'.format(len(mda_filenames)))
        ctime = datetime.datetime.fromtimestamp(os.path.getctime(mda_filenames[0]))
        print('First file created: {:}'.format(ctime))
        if debug:
            run = '2014-3'
            info = {
                    'user_id': 234567,
                    'badge':2000,
                    'first_name':'Megan',
                    'last_name':'Bourassa',
                    'email':'test@test.com',
                    'inst':'Northwestern University',
                    'inst_id': 9,
                    'proposal_title': 'Another Awesome experiment',
                    'proposal_id': '2001',
                    'experiment_type': 'GUP',
                    'start_time': datetime.datetime(2014, 12, 05, 10, 0, 0),
                    'end_time': datetime.datetime(2014, 12, 10, 10, 0, 0)
                    }
        else:
            run = schedule.findRunName(ctime, ctime)
            info = schedule.get_experiment_info(beamline=self.beamline, date=ctime)

        user = User.objects.get_or_create(
                username = info['badge'],
                first_name = info['first_name'],
                last_name = info['last_name'],
                email = info['email'],
                is_staff = False,
                is_superuser=False
                )
        if created:
            print('Created user: ', user)
        else:
            print('Existing user: ', user)
        user.save()

        user_profile, created = UserProfile.objects.get_or_create(
                user=user,
                badge=info['badge'],
                inst=info['inst'],
                inst_id=info['inst_id']
                )

        experiment, created = user.experiment.get_or_create(
                title=info['proposal_title'],
                proposal_id=info['proposal_id'],
                exp_type=info['experiment_type'],
                run=run,
                start_date=info['start_time'],
                end_date=info['end_time'],
                beamline=self.beamline
                )
        if created:
            print('Created experiment: ', experiment)
        else:
            print('Existing experiment: ', experiment)

        ignored_mda = []
        for mda_filename in mda_filenames:
            if experiment.scan.filter(scan_id=mda_filename.split('/')[-1].replace('.mda', '')).exists():
                # This file already entered in database
                print('Scan already in database')
                continue
            with transaction.atomic():
                mda = readMDA(mda_filename, maxdim=5, verbose=0)
                # Scan dimension?
                scan_dims = mda[0]['dimensions']
                if mda[1].scan_name.find('Fscan')>-1:
                    scan_type = 'fly'
                else:
                    scan_type='step'

                if len(scan_dims)==2 and scan_type=='step':
                    # 1D step scan
                    inner_scan = mda[1]
                    print('Entering 1D step scan')

                elif len(scan_dims)==2 and scan_type=='fly':
                    # 2D fly scan
                    inner_scan = mda[2]
                    outer_scan = mda[1]
                    print('Entering 2D fly scan')

                elif len(scan_dims)==3 and scan_type=='step':
                    # 2D step scan
                    inner_scan = mda[2]
                    outer_scan = mda[1]
                    print('Entering 2D step scan')
                else:
                    print('Could not recognise scan type: {:s}'.format(mda_filename))
                    ignored_mda.append(mda_filename)
                    continue

                # Check MDA integrity. Aborted scans will have incomplete dimensions.
                try:
                    assert inner_scan.scan_name is not ''
                    if len(scan_dims)>1:
                        assert outer_scan.scan_name is not ''

                except AssertionError:
                    # MDA data incomplete, will ignore
                    ignored_mda.append(mda_filename)
                    continue

                s = experiment.scan.create(
                    scan_id = mda_filename.split('/')[-1].replace('.mda', ''),
                    ts = datetime.datetime.fromtimestamp(os.path.getctime(mda_filename))
                )

                # History & Metadata
                s.history.create(dim=1, completed=inner_scan.curr_pt, requested=inner_scan.npts)
                if inner_scan.p[0].name is not '':
                    s.metadata.create(pvname=inner_scan.scan_name+'.P1PV', value=inner_scan.p[0].name)
                else:
                    s.metadata.create(pvname=inner_scan.scan_name+'.P1PV', value=inner_scan.p[0].desc)
                if len(scan_dims)>1:
                    s.history.create(dim=2, completed=outer_scan.curr_pt, requested=outer_scan.npts)
                    if outer_scan.p[0].desc is not '':
                        s.metadata.create(pvname=outer_scan.scan_name+'.P1PV', value=outer_scan.p[0].name)
                    else:
                        s.metadata.create(pvname=outer_scan.scan_name+'.P1PV', value=outer_scan.p[0].desc)

                # Detectors
                if scan_type=='step':
                    num_dets = len(inner_scan.d)
                    for det in range(num_dets):
                        s.detectors.create(active=det)
                        for row, scan_line in enumerate(inner_scan.d[det].data):
                            s.data.create(
                                    pvname=inner_scan.scan_name+'.D{:02d}DA'.format(inner_scan.d[det].number),
                                    name=inner_scan.d[det].name,
                                    row=row,
                                    value=scan_line
                                    )
                elif scan_type=='fly':

                    cfg = scans.config.fly_det_config['2-ID-E']
                    for det in cfg.keys():
                        int_det = int(det[1:])
                        if cfg[det]=='normal':
                            s.detectors.create(active=int_det)
                            for row, scan_line in enumerate(inner_scan.d[int_det].data):
                                s.data.create(
                                        pvname=inner_scan.scan_name+'.D{:02d}DA'.format(inner_scan.d[int_det].number),
                                        name=inner_scan.d[int_det].name,
                                        row=row,
                                        value=scan_line
                                        )
                        else:
                            base, filename = os.path.split(mda_filename)
                            base = '/'.join(base.split('/')[:-1])
                            h5_filename = filename.replace('.mda', '_2xfm3__.0h5')

                            if os.path.exists(os.path.join(base, 'flyXRF.h5')):
                                try:
                                    f=h5py.File(os.path.join(base, 'flyXRF.h5', h5_filename), 'r')
                                except IOError:
                                    continue
                            else:
                                # Data not yet quanitfied
                                continue
                            roi_num = cfg[det]
                            data = np.zeros(f['MAPS_RAW/data_a'].shape[1:])
                            for mca, channel in enumerate(['a','b','c','d']):
                                roilo = mda[0][scans.config.xfd_ioc_name['2-ID-E']+':mca{:d}.{:s}LO'.format(mca+1, roi_num)]
                                roihi = mda[0][scans.config.xfd_ioc_name['2-ID-E']+':mca{:d}.{:s}HI'.format(mca+1, roi_num)]
                                data += np.sum(f['MAPS_RAW/data_{:s}'.format(channel)].value[roilo:roihi,:,:])
                            scans.detectors.create(active=int_det)
                            for row, scan_line in enumerate(data):
                                scans.data.create(
                                        pvname=inner_scan.d[int_det].name,
                                        name=cfg[det],
                                        row=row,
                                        value=scan_line
                                        )


                # Analysed data
                base, filename = os.path.split(mda_filename)
                base = '/'.join(base.split('/')[:-1])
                h5_filename = filename.replace('mda', 'h5')

                if os.path.exists(base+'/img.dat/'+h5_filename):
                    with h5py.File(base+'/img.dat/'+h5_filename) as f:
                        # Add XRF
                        channel_names = f['MAPS/channel_names'].value
                        methods = [key for key in f['MAPS'].keys() if key.startswith('XRF') and not key.endswith('quant')]
                        for method in methods:
                            for c, channel_name in enumerate(channel_names):
                                for row, scan_line in enumerate(f['/'.join(['MAPS', method])].value[c,:,:]):
                                    s.data.create(pvname='_'.join([method, channel_name]), name=channel_name, row=row, value=scan_line)
                        # Add scalers
                        scaler_names = f['MAPS/scaler_names'].value
                        for j, scaler_name in enumerate(scaler_names):
                            for row, line in enumerate(f['MAPS/scalers'].value[j,:,:]):
                                s.data.create(pvname='_'.join(['scaler', scaler_name]), name=scaler_name, row=row, value=scan_line)


if __name__ == '__main__':
    imp= Importer('/run/media/david/data2/2014-3/bourassa')
    imp.run()

