# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ScanData'
        db.create_table(u'scans_scandata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('scan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scans.Scan'])),
            ('row', self.gf('django.db.models.fields.IntegerField')()),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'scans', ['ScanData'])

        # Deleting field 'Scan.value'
        db.delete_column(u'scans_scan', 'value')

        # Deleting field 'Scan.row'
        db.delete_column(u'scans_scan', 'row')


    def backwards(self, orm):
        # Deleting model 'ScanData'
        db.delete_table(u'scans_scandata')

        # Adding field 'Scan.value'
        db.add_column(u'scans_scan', 'value',
                      self.gf('django.db.models.fields.TextField')(default=None),
                      keep_default=False)

        # Adding field 'Scan.row'
        db.add_column(u'scans_scan', 'row',
                      self.gf('django.db.models.fields.IntegerField')(default=None),
                      keep_default=False)


    models = {
        u'scans.scan': {
            'Meta': {'object_name': 'Scan'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pvname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'scan_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'scans.scandata': {
            'Meta': {'object_name': 'ScanData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.IntegerField', [], {}),
            'scan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['scans.Scan']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['scans']