# Generated by Django 3.0.5 on 2020-05-05 22:51

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('right_ascension', models.FloatField(blank=True, null=True)),
                ('declination', models.FloatField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alert_identifier', models.CharField(max_length=200)),
                ('alert_timestamp', models.DateTimeField(blank=True, null=True)),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('role', models.CharField(blank=True, max_length=50, null=True)),
                ('message', django.contrib.postgres.fields.jsonb.JSONField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('topic_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='skip.Topic')),
            ],
        ),
        migrations.AddIndex(
            model_name='alert',
            index=models.Index(fields=['alert_timestamp'], name='alert_timestamp_idx'),
        ),
    ]
