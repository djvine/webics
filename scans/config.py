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

xfd_ioc_name = {
        '2-ID-B': '',
        '2-ID-E': 'dxpXMAP2xfm3',
        '2-ID-D': '',
        }

# Hacking together some way to specify the fly scan detectors so they display the same as the
# step scan detectors.
# Each detector channel (1-70) is either:
#   * 'normal' - ie at the end of each line read the D01DA PV to get the array
#   * 'roiN' - this channel should correspond to fluorescence detector ROI N.
#
# For 'roiN' read the RNLO and RNHI PVs to get the spectra channel range to sum.

fly_det_config = {
        '2-ID-E': {
                'D01':'normal', 'D02': 'normal', 'D03':'normal', 'D04':'normal', 'D05':'normal',
                'D06':'normal', 'D07': 'normal', 'D08':'normal', 'D09':'normal', 'D10':'normal',
                'D11':'normal', 'D12': 'normal', 'D13':'normal', 'D14':'normal', 'D15':'normal',
                'D16':'normal', 'D17': 'normal', 'D18':'normal', 'D19':'normal', 'D20':'normal',
                'D21':'normal', 'D22': 'normal', 'D23':'normal', 'D24':'normal', 'D25':'normal',
                'D26':'normal', 'D27': 'normal', 'D28':'normal', 'D29':'normal', 'D30':'normal',
                'D31':'R1', 'D32':'R2', 'D33':'R3', 'D34':'R4', 'D35':'R5',
                'D36':'R6', 'D37':'R7', 'D38':'R8', 'D39':'R9', 'D40':'R10',
                'D41':'R11', 'D42':'R12', 'D43':'R13', 'D44':'R14', 'D45':'R15',
                'D46':'R16', 'D47':'R17', 'D48':'R18', 'D49':'R19', 'D50':'R20',
                'D51':'R21', 'D52':'R22', 'D53':'R23', 'D54':'R24', 'D55':'R25',
                'D56':'R26', 'D57':'R27', 'D58':'R28', 'D59':'R29', 'D60':'R30',
                #'D61':'R21', 'D62':'R22', 'D63':'R23', 'D64':'R24', 'D65':'R25',
                #'D66':'R26', 'D67':'R27', 'D68':'R28', 'D69':'R29', 'D70':'R30',
            }
    }
