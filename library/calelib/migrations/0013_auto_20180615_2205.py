# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-15 19:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calelib', '0012_task_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='time_at',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
