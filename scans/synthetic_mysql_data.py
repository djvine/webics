from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
from django.utils import timezone
import cPickle
import numpy as np
from numpy.random import random
import ipdb


scans = []
for i in range(10):
	scans.append(Scan(beamline='djv', scan_id='djv_{:04d}'.format(i), ts=timezone.now()))
	scans[i].save()

for i, s in enumerate(scans):
	s.scanhistory_set.create(dim=0, completed=11)
	if i%2==0:
		s.scanhistory_set.create(dim=1, completed=21)
	for det in range(5,10):
		s.scandetectors_set.create(active=det)
		s.scandata_set.create(pvname='djv:scan1.D{:02d}DA'.format(det), row=0, value=str(cPickle.dumps(random((11)))))
		if i%2==0:
			for j in range(1,11):
				s.scandata_set.create(pvname='djv:scan1.D{:02d}DA'.format(det), row=j, value=str(cPickle.dumps(random((11)))))
	s.scanmetadata_set.create(pvname='djv:scan1.P1PV', value='Sample X')
	s.scanmetadata_set.create(pvname='djv:scan2.P1PV', value='Sample Y')
