# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-11 17:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calelib', '0003_auto_20180611_0235'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plan',
            name='_time_at',
        ),
        migrations.AddField(
            model_name='plan',
            name='time_at',
            field=models.TimeField(null=True),
        ),
    ]
