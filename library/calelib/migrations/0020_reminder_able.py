# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-16 01:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calelib', '0019_plan_able'),
    ]

    operations = [
        migrations.AddField(
            model_name='reminder',
            name='able',
            field=models.BooleanField(default=True),
        ),
    ]
