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
            ('pvname', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('row', self.gf('django.db.models.fields.IntegerField')()),
            ('scan_id', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'scans', ['Scan'])


    def backwards(self, orm):
        # Deleting model 'Scan'
        db.delete_table(u'scans_scan')


    models = {
        u'scans.scan': {
            'Meta': {'object_name': 'Scan'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pvname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'row': ('django.db.models.fields.IntegerField', [], {}),
            'scan_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['scans']