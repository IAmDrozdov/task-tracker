# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-13 02:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calelib', '0006_auto_20180612_0209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=1),
        ),
    ]
