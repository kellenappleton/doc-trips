# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-22 18:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0016_auto_20170122_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalapplication',
            name='croo_willing',
            field=models.BooleanField(verbose_name='I would like to be considered for a Croo position. I understand...'),
        ),
        migrations.AlterField(
            model_name='generalapplication',
            name='leader_willing',
            field=models.BooleanField(verbose_name='I would like to be considered for a Trip Leader position. I understand... (describe commitments, etc.)'),
        ),
    ]
