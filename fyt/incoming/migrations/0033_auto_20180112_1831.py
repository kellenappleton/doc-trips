# Generated by Django 2.0.1 on 2018-01-12 23:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0032_auto_20170814_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingstudent',
            name='registration',
            field=models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='trippee', to='incoming.Registration'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='user',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
