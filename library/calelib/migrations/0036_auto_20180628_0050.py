# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-27 21:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calelib', '0035_auto_20180628_0049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='parent_task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subtasks', to='calelib.Task'),
        ),
    ]
