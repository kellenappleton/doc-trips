# Generated by Django 2.0.3 on 2018-04-02 21:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0087_auto_20180402_1454'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scoreclaim',
            options={'ordering': ['claimed_at']},
        ),
    ]
