from django.db import models
from django.utils import timezone
import datetime
import cPickle

# Create your models here.

class Scan(models.Model):
    pvname = models.CharField('PV Name', max_length=200)
    beamline = models.CharField('Beamline', max_length=200)     
    scan_id = models.CharField('Scan ID', max_length=256)
    ts = models.DateTimeField('Scan Initiated', auto_now_add=True)

    def __unicode__(self):
        return '{0:s}: {1:s}'.format(self.pvname, str(self.ts))

    def is_recent_scan(self):
        return self.ts >= timezone.now() - datetime.timedelta(days=1)

    is_recent_scan.admin_order_field = 'ts'
    is_recent_scan.boolean = True
    is_recent_scan.short_description = 'Recent scan?'



class ScanData(models.Model):
    scan = models.ForeignKey(Scan)
    row = models.IntegerField('Scan Row')
    value = models.TextField('Scan Value')

    def __unicode__(self):
        
        return '{0:s} row: {1:d}'.format(self.scan.pvname, self.row)