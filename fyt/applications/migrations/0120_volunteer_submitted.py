# Generated by Django 2.1.5 on 2019-01-23 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0119_remove_volunteer_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteer',
            name='submitted',
            field=models.DateTimeField(default=None, editable=False, null=True),
        ),
    ]
