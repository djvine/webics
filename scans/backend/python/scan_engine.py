import os
import multiprocessing as mp

# EPICS
import epics
# django
os.environ['DJANGO_SETTINGS_MODULE'] = 'webics.settings'
import django
from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
# redis
import redis

pvs = {} # pvname: pv
total_jobs = 0
queue = mp.JoinableQueue()
results = mp.Queue()
num_processes = mp.cpu_count()
tup = (queue, results)
semaphore = {}


def init_scan(ioc_name):
	pref1d = ioc_name+':scan1'
	pref2d = ioc_name+':scan2'

	# connect to PVs
	epics_connect(pref1d+'.EXSC')
	epics_connect(pref2d+'.EXSC')

	epics_connect(ioc_name+':ScanDim.VAL', auto_monitor=True, callback=cb)
	# The following PVs are used to generate the scan_id
    epics_connect(ioc_name+':saveData_fileSystem')
    epics_connect(ioc_name+':saveData_subDir')
    epics_connect(ioc_name+':saveData_baseName')
    epics_connect(ioc_name+':saveData_scanNumber')

    # Monitoring the following PVs is the only way to reliably get the P1PA
    # P1RA only gets updated to the correct value at the end of the scan line - don't use it.
    for pref in [pref1d, pref2d]:
	    epics_connect(pref+'.P1PV')
	    epics_connect(pref+'.P1SP')
	    epics_connect(pref+'.P1EP')
	    epics_connect(pref+'.NPTS')
	    epics_connect(pref+'.P1RA')

    # Get the current point and row number
    epics_connect(pref2d+'.CPT')

    # Get the detector PVs
    for i in range(1,71):
        epics_connect(pref1d+'.D{:02d}NV'.format(i))
        epics_connect(pref1d+'.D{:02d}PV'.format(i))
        epics_connect(pref1d+'.D{:02d}CA'.format(i))

def epics_connect(self, pvname, auto_monitor=False, callback=None):
    if pvs.has_key(pvname):
        return pvs[pvname]
    
    p = epics.PV(pvname, auto_monitor=auto_monitor)
    if callback:
    	p.add_callback(callback)
    epics.poll()
    if p.connected:
        pvs[pvname] = p
    else:
    	print '{:s} Not Connected'.format(pvname)

def cb(pvname, value, **kwargs):
	queue.put((pvname, value))
	total_jobs += 1

def scan_control(*args, **kwargs):

def check_connectedness():
	# Check if pvs are connected
	# - Reconnect if possible
	pass

def mainloop():

	for beamline in scan.config.beamlines:
		init_scan(beamline)

	processes = [mp.Process(target=scan_control,
            		args=tup) for i in range(num_processes)]

	for process in self.p:
	    process.start()

	while True:
