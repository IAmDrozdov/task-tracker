# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-11 23:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calelib', '0005_auto_20180611_2332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='deadline',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]