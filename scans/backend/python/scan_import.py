#!/usr/bin/env python
import os
import time
import threading
import ipdb
import numpy as np
import datetime
# django
import django
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import scans.config
from scans.models import User, Experiment, Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata, flush_transaction
from beamon import schedule

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

class Importer(threading.Thread):

    def __init__(self, directory):
        self.directory = directory
        self.beamline = '2-ID-E'

    def run(self):
        if not os.path.exists(os.path.join(self.directory, 'mda')):
            print('Could not find mda directory. Exiting')
            sys.exit(1)

        mda_filenames = glob.glob(os.path.join(self.directory, 'mda/*.mda'))
        print('Found {:d} mda files.'.format(len(mda_filenames)))
        ctime = os.path.getctime(mda_filenames[0])
        print('First file created: {:}'.format(ctime))
        run = schedule.findRunName(ctime, ctime)
        info = schedule.get_experiment_info(beamline=self.beamline, date=ctime)

        user, created = User.objects.get_or_create(
                user_id=info['user_id'],
                badge=info['badge'],
                first_name=info['first_name'],
                last_name=info['last_name'],
                email=info['email'],
                inst=info['inst'],
                inst_id=info['inst_id']
                )
        if created:
            print('Created user: ', user)
        else:
            print('Existing user: ', user)
        user.save()
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
            with transaction.atomic():
                s = experiment.scan.create(
                    scan_id = mda_filename.split('/')[-1].strip('.mda'),
                    ts = os.path.getctime(mda_filename)
                )
                mda = readMDA(mda_filename, maxdim=5, verbose=0)
                # Scan dimension?
                scan_dims = mda[0]['dimensions']
                if mda[1].scan_name.find('Fscan')>-1:
                    scan_type = 'fly'
                else:
                    scan_type='step'

                if len(scan_dims)==1 and scan_type=='step':
                    # 1D step scan
                    inner_scan = mda[1]

                elif len(scan_dims)==2 and scan_type=='fly':
                    # 2D fly scan
                    inner_scan = mda[2]
                    outer_scan = mda[1]

                elif len(scan_dims)==3 and scan_type=='step':
                    # 2D step scan
                    inner_scan = mda[2]
                    outer_scan = mda[3]
                else:
                    print('Could not recognise scan type: {:s}'.format(mda_filename))
                    continue

                # History & Metadata
                s.history.create(dim=1, completed=inner_scan.curr_pt, requested=inner_scan.npts)
                if inner_scan.p[0].desc is '':
                    s.metadata.create(pvname=inner_scan.scan_name+'.P1PV', value=inner_scan.p[0].name)
                else:
                    s.metadata.create(pvname=inner_scan.scan_name+'.P1PV', value=inner_scan.p[0].desc)
                if len(scan_dims)>1:
                    s.history.create(dim=2, completed=outer_scan.curr_pt, requested=outer_scan.npts)
                    if outer_scan.p[0].desc is '':
                        s.metadata.create(pvname=outer_scan.scan_name+'.P1PV', value=outer_scan.p[0].name)
                    else:
                        s.metadata.create(pvname=outer_scan.scan_name+'.P1PV', value=outer_scan.p[0].desc)

                # Detectors
                if scan_type=='step':
                    num_dets = len(getattr(inner_scan, d))
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
                        if cfg[det]=='normal':
                            s.detectors.create(active=det)
                            for row, scan_line in enumerate(inner_scan.d[det].data):
                                s.data.create(
                                        pvname=inner_scan.scan_name+'.D{:02d}DA'.format(inner_scan.d[det].number),
                                        name=inner_scan.d[det].name,
                                        row=row,
                                        value=scan_line
                                        )
                        else:
                            base, filename = os.path.split(moda_filename)
                            base = '/'.join(base.split('/')[:-1])
                            h5_filename = filename.replace('.mda', '_2xfm3__.0h5')

                            if os.path.exists(os.path.join([base, 'flyXRF.h5'])):
                                try:
                                    f=h5py.File(os.path.join([base, 'flyXRF.h5', h5_filename]), 'r')
                                except IOError:
                                    continue
                            roi_num = cfg[det]
                            data = np.zeros(f['MAPS_RAW/data_a'].shape[1:])
                            for mca, channel in enumerate(['a','b','c','d']):
                                roilo = mda[0][scans.config.xfd_ioc_name['2-ID-E']+':mca{:d}.{:s}LO'.format(mca+1, roi_num)]
                                roihi = mda[0][scans.config.xfd_ioc_name['2-ID-E']+':mca{:d}.{:s}HI'.format(mca+1, roi_num)]
                                data += np.sum(f['MAPS_RAW/data_{:s}'.format(channel)].value[roilo:roihi,:,:])
                            scans.detectors.create(active=det)
                            for row, scan_line in enumerate(data):
                                scans.data.create(
                                        pvname=inner_scan.d[det].name,
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
                        methods = [key for key in f['MAPS'].keys() if key.startswith('XRF')]
                        for method in methods:
                            for c, channel_name in enumerate(channel_names):
                                for row, scan_line in enumerate(f['/'.join(['MAPS', method])].value[c,:,:]):
                                    s.data.create(pvname=method, name=channel_name, row=row, value=base64.b64encode(scan_line))
                        # Add scalers
                        for j, scaler_name in enumerate(scaler_names):
                            for row, line in enumerate(f['MAPS/scalers'].value[j,:,:]):
                                s.data.create(pvname='scalers', name=scaler_name, row=row, value=base64.b64encode(scan_line))



