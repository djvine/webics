import os
import multiprocessing as mp
import signal
import sys

# EPICS
import epics
# django
os.environ['DJANGO_SETTINGS_MODULE'] = 'webics.settings'
import django
from scans.models import Scan, ScanHistory, ScanDetectors, ScanData, ScanMetadata
# redis
import redis

total_jobs = 0
queue = mp.JoinableQueue()
num_processes = mp.cpu_count()
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
    
    p = epics.PV(pvname, auto_monitor=auto_monitor)
    if callback:
    	p.add_callback(callback)
    epics.poll()
    if p.connected:
        pvs[pvname] = p
    else:
    	print '{:s} Not Connected'.format(pvname)
    return p

def cb(pvname, value, **kwargs):
	queue.put((pvname, value))
	total_jobs += 1

@worker
def scan_control(*args, **kwargs):
    print args
    ioc_name = args[0].split(':')[0]

    pref1d = ioc_name+':scan1'
    pref2d = ioc_name+':scan2'

    scan_dim = args[1]
    if scan_dim == 1: # 1d scan w/no fluorescence detector
        pass
    elif scan_dim == 2: # 2d scan w/no fluorescence detector OR 1d scan w/fluorescence detector
        pass
    elif scan_dim == 3: # 2d scan w/ fluorescence detector
        pass

    scan_id = 

def check_connectedness():
	# Check if pvs are connected
	# - Reconnect if possible
	pass


def signal_handler(signal, frame):
    # catch ctrl-c and exit gracefully
    
    # Add poison pills to kill processes
    for i in range(num_processes):
        queue.put((None,))

    sys.exit(0)

def mainloop():
    # Register for SIGINT before entering infinite loop
    signal.signal(signal.SIGINT, signal_handler)

	for beamline in scan.config.beamlines:
		init_scan(beamline)

	processes = [mp.Process(target=scan_control,
            		args=queue) for i in range(num_processes)]

	for process in self.p:
	    process.start()

	queue.join()

    queue.close()

    for process in processes:
        process.join()


def worker(func):

    def worker2(*args, **kwargs):
        name = mp.current_process().name
        jobs_completed = 0
        jobs = args[0]
        while True:
            job_args = jobs.get()
            print '{:s} Enagaged: Scan {:s}'.format(name, job_args[0].split(':')[0])
            if job_args[0] is None:  # Deal with Poison Pill
                jobs.task_done()
                break

            func(job_args)
            print '{:s} Disengaged: Completed Scan {:s}'.format(name, job_args[0].split(':')[0])
            jobs_completed += 1
            jobs.task_done()
        return worker2
    return worker2