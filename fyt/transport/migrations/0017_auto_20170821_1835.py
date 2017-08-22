# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-21 22:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0016_merge_20170821_1727'),
    ]

    operations = [
        migrations.RenameField(
            model_name='internalbus',
            old_name='custom_times',
            new_name='use_custom_times',
        ),
        migrations.AlterField(
            model_name='stoporder',
            name='custom_time',
            field=models.TimeField(default=None, null=True, verbose_name='Custom pickup/dropoff time'),
        ),
    ]