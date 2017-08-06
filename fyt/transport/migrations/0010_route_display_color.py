# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-16 21:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0009_auto_20170716_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='display_color',
            field=models.CharField(default='white', help_text='The color to use when displaying this route in tables.', max_length=20),
        ),
    ]