# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import scans.pickled_object


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name=b'Proposal Title')),
                ('proposal_id', models.IntegerField(verbose_name=b'Proposal ID')),
                ('exp_type', models.CharField(default=b'GUP', max_length=3, verbose_name=b'Experiment Type', choices=[(b'GUP', b'General User Program'), (b'PUP', b'Partner User Program'), (b'RA', b'Rapid-Access')])),
                ('run', models.CharField(max_length=10, verbose_name=b'Run')),
                ('start_date', models.DateTimeField(verbose_name=b'Start date')),
                ('end_date', models.DateTimeField(verbose_name=b'End date')),
                ('beamline', models.CharField(max_length=200, verbose_name=b'Beamline')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scan_id', models.CharField(max_length=255, verbose_name=b'Scan ID')),
                ('ts', models.DateTimeField(auto_now_add=True, verbose_name=b'Scan Initiated')),
                ('experiment', models.ForeignKey(related_name='scan', to='scans.Experiment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScanData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=255, verbose_name=b'Name')),
                ('pvname', models.CharField(max_length=255, verbose_name=b'PV name')),
                ('row', models.IntegerField(verbose_name=b'Scan Row')),
                ('value', scans.pickled_object.PickledObjectField(verbose_name=b'Value', null=True, editable=False)),
                ('scan', models.ForeignKey(related_name='data', to='scans.Scan')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScanDetectors',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.IntegerField(verbose_name=b'Valid Scan Record Detector Number')),
                ('scan', models.ForeignKey(related_name='detectors', to='scans.Scan')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScanHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dim', models.IntegerField(verbose_name=b'Scan Dimension')),
                ('completed', models.IntegerField(verbose_name=b'Points Completed')),
                ('requested', models.IntegerField(verbose_name=b'Points Requested')),
                ('scan', models.ForeignKey(related_name='history', to='scans.Scan')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScanMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pvname', models.CharField(max_length=256, verbose_name=b'PV name')),
                ('value', models.TextField(verbose_name=b'Scan Value')),
                ('scan', models.ForeignKey(related_name='metadata', to='scans.Scan')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField(unique=True, verbose_name=b'User ID')),
                ('badge', models.IntegerField(verbose_name=b'Badge')),
                ('first_name', models.CharField(max_length=100, verbose_name=b'First Name')),
                ('last_name', models.CharField(max_length=100, verbose_name=b'Last Name')),
                ('email', models.CharField(max_length=100, verbose_name=b'Email')),
                ('inst_id', models.IntegerField(verbose_name=b'Insitution ID')),
                ('inst', models.CharField(max_length=200, verbose_name=b'Institution')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='scandata',
            unique_together=set([('scan', 'pvname', 'row')]),
        ),
        migrations.AlterUniqueTogether(
            name='scan',
            unique_together=set([('scan_id', 'experiment')]),
        ),
        migrations.AddField(
            model_name='experiment',
            name='user',
            field=models.ForeignKey(related_name='experiment', to='scans.User'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='experiment',
            unique_together=set([('user', 'beamline', 'start_date')]),
        ),
    ]
