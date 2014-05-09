# SYNTAX beamline: ioc_name
import socket
hostname = socket.gethostname()

if hostname in ['lemon.xray.aps.anl.gov', 'joule-vm.xray.aps.anl.gov']:
	ioc_names = {
		'2-ID-B': '2idb1',
		'2-ID-E': '2xfm',
	}
elif hostname in ['dusk', 'dawn']:

	ioc_names = {
		'DJV': 'djv',
		'2-ID-B': '2idb1',
		#'2-ID-D': '2idd',
	}
