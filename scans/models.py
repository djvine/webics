from django.db import models
from django.utils import timezone
import datetime
import cPickle
from django.db import transaction, connections

@transaction.commit_manually
def flush_transaction():
    """
    Flush the current transaction so we don't read stale data

    Use in long running processes to make sure fresh data is read from
    the database.  This is a problem with MySQL and the default
    transaction mode.  You can fix it by setting
    "transaction-isolation = READ-COMMITTED" in my.cnf or by calling
    this function at the appropriate moment
    """
    for conn in connections.all():
        conn.connection.ping(True)
    transaction.commit()

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
    scan = models.ForeignKey(Scan, related_name='history')
    dim = models.IntegerField('Scan Dimension')
    completed = models.IntegerField('Points Completed')
    requested = models.IntegerField('Points Requested')

class ScanDetectors(models.Model):
    scan = models.ForeignKey(Scan, related_name='detectors')
    active = models.IntegerField('Valid Scan Record Detector Number')

class ScanData(models.Model):
    scan = models.ForeignKey(Scan, related_name='data')
    pvname = models.CharField('PV name', max_length=256)
    row = models.IntegerField('Scan Row')
    value = models.TextField('Scan Value')

    def __unicode__(self):
        
        return '{0:s} row: {1:d}'.format(self.pvname, self.row)

class ScanMetadata(models.Model):
    scan = models.ForeignKey(Scan, related_name='metadata')
    pvname = models.CharField('PV name', max_length=256)
    value = models.TextField('Scan Value')