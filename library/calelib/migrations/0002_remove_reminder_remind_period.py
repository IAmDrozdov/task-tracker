# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-03 21:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('calelib', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reminder',
            name='remind_period',
        ),
    ]
