from django.db import models, transaction, connections
from django.contrib.auth.models import User
from django.utils import timezone
from pickled_object import PickledObjectField
import datetime

def flush_transaction():
    """
    Flush the current transaction so we don't read stale data

    Use in long running processes to make sure fresh data is read from
    the database.  This is a problem with MySQL and the default
    transaction mode.  You can fix it by setting
    "transaction-isolation = READ-COMMITTED" in my.cnf or by calling
    this function at the appropriate moment
    """
    transaction.set_autocommit(False)
    try:
        for conn in connections.all():
            conn.connection.ping(True)
        transaction.commit()
    finally:
        transaction.set_autocommit(True)

class Experiment(models.Model):

    experiment_types = (
            ('GUP', 'General User Program'),
            ('PUP', 'Partner User Program'),
            ('RA', 'Rapid-Access')
            )

    user = models.ForeignKey(User, related_name='experiment')
    title = models.CharField('Proposal Title', max_length=255)
    proposal_id = models.IntegerField('Proposal ID')
    exp_type = models.CharField('Experiment Type', max_length=3, choices=experiment_types, default='GUP')
    run = models.CharField('Run', max_length=10)
    start_date = models.DateTimeField('Start date')
    end_date = models.DateTimeField('End date')
    beamline = models.CharField('Beamline', max_length=200)

    def __unicode__(self):
        return '<{:s} {:s}> {:s}'.format(self.run, self.beamline, self.user.last_name)

    class Meta:
        unique_together = ('user', 'beamline', 'start_date')

class UserProfile(models.Model):

    user = models.ForeignKey(User, related_name='profile')
    aps_user_id = models.IntegerField('User ID', unique=True)
    badge = models.IntegerField('Badge', unique=True)
    inst_id = models.IntegerField('Insitution ID')
    inst = models.CharField('Institution', max_length=200)

    def __unicode__(self):
        return '<{:d}> {:s}'.format(self.user_id, self.user.last_name)


class Scan(models.Model):
    experiment = models.ForeignKey(Experiment, related_name='scan')
    scan_id = models.CharField('Scan ID', max_length=255)
    ts = models.DateTimeField('Scan Initiated', auto_now_add=True)

    class Meta:
        unique_together = ('scan_id', 'experiment')

    def __unicode__(self):
        return '{0:s}: {1:s}'.format(str(self.ts), self.scan_id)

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
    name = models.CharField('Name', max_length=255, default='')
    pvname = models.CharField('PV name', max_length=255)
    row = models.IntegerField('Scan Row')
    value = PickledObjectField('Value')

    class Meta:
        unique_together = ('scan', 'pvname', 'row')

    def __unicode__(self):
        return '{0:s} row: {1:d}'.format(self.pvname, self.row)

class ScanMetadata(models.Model):
    scan = models.ForeignKey(Scan, related_name='metadata')
    pvname = models.CharField('PV name', max_length=256)
    value = models.TextField('Scan Value')
