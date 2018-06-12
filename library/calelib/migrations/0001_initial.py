# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-03 14:08
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info', models.CharField(max_length=100)),
                ('created', models.BooleanField(default=False)),
                ('last_create', models.DateField(auto_now=True)),
                ('_time_at', django.contrib.postgres.fields.jsonb.JSONField(db_column='time_at', null=True)),
                ('period_type', models.CharField(choices=[('d', 'day'), ('wd', 'week'), ('m', 'month'), ('y', 'year')], max_length=6)),
                ('_period', django.contrib.postgres.fields.jsonb.JSONField(db_column='period', default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remind_before', models.IntegerField(default=0)),
                ('remind_type', models.CharField(choices=[('m', 'minutes'), ('h', 'hours'), ('d', 'days'), ('mth', 'months')], max_length=6)),
                ('remind_period', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), default=list, size=None)),
                ('priority', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('deadline', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(default='UNFINISHED', max_length=10)),
                ('archived', models.BooleanField(default=False)),
                ('performers', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), default=list, size=None)),
                ('plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='calelib.Plan')),
                ('subtasks', models.ManyToManyField(to='calelib.Task')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(max_length=20, unique=True)),
                ('plans', models.ManyToManyField(to='calelib.Plan')),
                ('reminders', models.ManyToManyField(to='calelib.Reminder')),
                ('tasks', models.ManyToManyField(to='calelib.Task')),
            ],
        ),
        migrations.AddField(
            model_name='reminder',
            name='tasks',
            field=models.ManyToManyField(to='calelib.Task'),
        ),
    ]
