# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-08 18:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0060_auto_20170301_1719'),
    ]

    operations = [
        migrations.RenameField(
            model_name='volunteer',
            old_name='from_where',
            new_name='hometown',
        ),
    ]