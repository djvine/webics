# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Scan'
        db.create_table(u'scans_scan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('beamline', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('scan_id', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'scans', ['Scan'])

        # Adding model 'ScanHistory'
        db.create_table(u'scans_scanhistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scan', self.gf('django.db.models.fields.related.ForeignKey')(related_name='history', to=orm['scans.Scan'])),
            ('dim', self.gf('django.db.models.fields.IntegerField')()),
            ('completed', self.gf('django.db.models.fields.IntegerField')()),
            ('requested', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'scans', ['ScanHistory'])

        # Adding model 'ScanDetectors'
        db.create_table(u'scans_scandetectors', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scan', self.gf('django.db.models.fields.related.ForeignKey')(related_name='detectors', to=orm['scans.Scan'])),
            ('active', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'scans', ['ScanDetectors'])

        # Adding model 'ScanData'
        db.create_table(u'scans_scandata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scan', self.gf('django.db.models.fields.related.ForeignKey')(related_name='data', to=orm['scans.Scan'])),
            ('pvname', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('row', self.gf('django.db.models.fields.IntegerField')()),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'scans', ['ScanData'])

        # Adding model 'ScanMetadata'
        db.create_table(u'scans_scanmetadata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scan', self.gf('django.db.models.fields.related.ForeignKey')(related_name='metadata', to=orm['scans.Scan'])),
            ('pvname', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'scans', ['ScanMetadata'])


    def backwards(self, orm):
        # Deleting model 'Scan'
        db.delete_table(u'scans_scan')

        # Deleting model 'ScanHistory'
        db.delete_table(u'scans_scanhistory')

        # Deleting model 'ScanDetectors'
        db.delete_table(u'scans_scandetectors')

        # Deleting model 'ScanData'
        db.delete_table(u'scans_scandata')

        # Deleting model 'ScanMetadata'
        db.delete_table(u'scans_scanmetadata')


    models = {
        u'scans.scan': {
            'Meta': {'object_name': 'Scan'},
            'beamline': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scan_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'scans.scandata': {
            'Meta': {'object_name': 'ScanData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pvname': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'row': ('django.db.models.fields.IntegerField', [], {}),
            'scan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'data'", 'to': u"orm['scans.Scan']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'scans.scandetectors': {
            'Meta': {'object_name': 'ScanDetectors'},
            'active': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'detectors'", 'to': u"orm['scans.Scan']"})
        },
        u'scans.scanhistory': {
            'Meta': {'object_name': 'ScanHistory'},
            'completed': ('django.db.models.fields.IntegerField', [], {}),
            'dim': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requested': ('django.db.models.fields.IntegerField', [], {}),
            'scan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'history'", 'to': u"orm['scans.Scan']"})
        },
        u'scans.scanmetadata': {
            'Meta': {'object_name': 'ScanMetadata'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pvname': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'scan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metadata'", 'to': u"orm['scans.Scan']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['scans']