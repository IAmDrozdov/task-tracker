# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-20 18:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calelib', '0029_auto_20180620_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='users',
            field=models.ManyToManyField(related_name='tasks', related_query_name='task', to='calelib.Customer'),
        ),
    ]
