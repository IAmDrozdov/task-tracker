# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-13 02:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calelib', '0009_auto_20180613_0554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='deadline',
            field=models.DateTimeField(blank=True, default=None, help_text='When you will lose task', null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='info',
            field=models.CharField(help_text='Enter what to do', max_length=100),
        ),
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=1, help_text='Need for speed'),
        ),
        migrations.AlterField(
            model_name='task',
            name='tags',
            field=models.CharField(blank=True, help_text='Some grouping info', max_length=20, null=True),
        ),
    ]
