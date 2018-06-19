# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-19 17:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calelib', '0022_auto_20180619_1946'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='tasks',
        ),
        migrations.AlterField(
            model_name='task',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='calelib.Customer'),
        ),
    ]
