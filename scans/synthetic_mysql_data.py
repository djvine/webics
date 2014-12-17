from scans.models import User, Experiment, Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
from django.utils import timezone
import cPickle
import numpy as np
from numpy.random import random
import ipdb
import datetime as dt
from beamon import schedule
import base64
dates = [dt.datetime(2014,12,10,10,0,0), dt.datetime(2014,12,3,10,0,0)]

bl = '2-ID-E'

for date in dates:
    run = schedule.findRunName(date, date)
    info = schedule.get_experiment_info(beamline=bl, date=date)
    ipdb.set_trace()
    user, created = User.objects.get_or_create(
            user_id=info['user_id'],
            badge=info['badge'],
            first_name=info['first_name'],
            last_name=info['last_name'],
            email=info['email'],
            inst=info['inst'],
            inst_id=info['inst_id']
            )
    user.save()
    experiment, created = user.experiment.get_or_create(
            title=info['proposal_title'],
            proposal_id=info['proposal_id'],
            exp_type=info['experiment_type'],
            run=run,
            start_date=info['start_time'],
            end_date=info['end_time'],
            beamline=bl
            )

    scans = []
    for i in range(10):
        scans.append(experiment.scan.create( scan_id='djv_{:04d}'.format(i), ts=timezone.now()))
        scans[i].save()

    for i, s in enumerate(scans):
        s.history.create(dim=0, completed=11, requested=11)
        if i%2==0:
            s.history.create(dim=1, completed=21, requested=21)
        for det in range(5,10):
            s.detectors.create(active=det)
            s.data.create(pvname='djv:scan1.D{:02d}DA'.format(det), row=0, value=base64.b64encode(random(11)))
            if i%2==0:
                for j in range(1,11):
                    s.data.create(pvname='djv:scan1.D{:02d}DA'.format(det), row=j, value=base64.b64encode(random(11)))
        s.metadata.create(pvname='djv:scan1.P1PV', value='Sample X')
        s.metadata.create(pvname='djv:scan2.P1PV', value='Sample Y')

