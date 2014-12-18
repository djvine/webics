# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scans', '0002_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(default=b'u', max_length=1, null=True, verbose_name=b'Role', choices=[(b'u', b'User'), (b'a', b'admin')]),
            preserve_default=True,
        ),
    ]
