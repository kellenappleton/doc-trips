# Generated by Django 2.0.2 on 2018-03-03 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0020_firstaidcertification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firstaidcertification',
            name='name',
            field=models.CharField(blank=True, choices=[(None, '--'), ('FA', 'First Aid'), ('CPR', 'CPR'), ('WFA', 'WFA'), ('WFR', 'WFR'), ('W-EMT', 'W-EMT'), ('EMT', 'EMT'), ('OEC', 'OEC'), ('other', 'other')], default='', max_length=10),
        ),
    ]
