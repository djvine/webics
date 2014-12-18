# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scans', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(default=b'u', max_length=1, verbose_name=b'Role', choices=[(b'u', b'User'), (b'a', b'admin')]),
            preserve_default=True,
        ),
    ]
