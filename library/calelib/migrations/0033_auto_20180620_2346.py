# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-20 20:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calelib', '0032_customer_shared_tasks'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='performers',
        ),
        migrations.AlterField(
            model_name='customer',
            name='shared_tasks',
            field=models.ManyToManyField(related_name='performers', to='calelib.Task'),
        ),
    ]
