from django.db import models
from django.utils import timezone
import datetime
import cPickle

# Create your models here.

class Scan(models.Model):
    beamline = models.CharField('Beamline', max_length=200)     
    scan_id = models.CharField('Scan ID', max_length=256)
    ts = models.DateTimeField('Scan Initiated', auto_now_add=True)

    def __unicode__(self):
        return '{0:s}: {1:s} {2:s}'.format(str(self.ts), self.beamline, self.scan_id)

    def is_recent_scan(self):
        return self.ts >= timezone.now() - datetime.timedelta(days=1)

    is_recent_scan.admin_order_field = 'ts'
    is_recent_scan.boolean = True
    is_recent_scan.short_description = 'Recent scan?'

class ScanHistory(models.Model):
    scan = models.ForeignKey(Scan)
    dim = models.IntegerField('Scan Dimension')
    completed = models.IntegerField('Points Completed')

class ScanDetectors(models.Model):
    scan = models.ForeignKey(Scan)
    active = models.IntegerField('Valid Scan Record Detector Number')

class ScanData(models.Model):
    scan = models.ForeignKey(Scan)
    pvname = models.CharField('PV name', max_length=256)
    row = models.IntegerField('Scan Row')
    value = models.TextField('Scan Value')

    def __unicode__(self):
        
        return '{0:s} row: {1:d}'.format(self.pvname, self.row)

class ScanMetadata(models.Model):
    scan = models.ForeignKey(Scan)
    pvname = models.CharField('PV name', max_length=256)
    value = models.TextField('Scan Value')