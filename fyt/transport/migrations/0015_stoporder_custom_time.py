# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-21 21:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0014_internalbus_dirty'),
    ]

    operations = [
        migrations.AddField(
            model_name='stoporder',
            name='custom_time',
            field=models.TimeField(default=None, null=True, verbose_name='Custom time'),
        ),
    ]
