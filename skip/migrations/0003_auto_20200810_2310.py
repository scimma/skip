# Generated by Django 3.1 on 2020-08-10 23:10

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('skip', '0002_auto_20200810_2300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alert',
            name='declination',
        ),
        migrations.RemoveField(
            model_name='alert',
            name='right_ascension',
        ),
        migrations.AddField(
            model_name='alert',
            name='coordinates',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]
