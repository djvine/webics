# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Scan.beamline'
        db.add_column(u'scans_scan', 'beamline',
                      self.gf('django.db.models.fields.CharField')(default=None, max_length=200),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Scan.beamline'
        db.delete_column(u'scans_scan', 'beamline')


    models = {
        u'scans.scan': {
            'Meta': {'object_name': 'Scan'},
            'beamline': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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