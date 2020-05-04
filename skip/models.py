import json

from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.


class Target(models.Model):
    name = models.CharField(max_length=200)
    right_ascension = models.FloatField(null=True, blank=True)
    declination = models.FloatField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Event(models.Model):
    # target_id = models.ForeignKey(Target, on_delete=models.CASCADE)
    event_identifier = models.CharField(max_length=200)
    event_timestamp = models.DateTimeField(null=True, blank=True)
    right_ascension = models.FloatField(null=True, blank=True)
    declination = models.FloatField(null=True, blank=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    topic = models.CharField(max_length=50)
    message = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


    class Meta:
        indexes = [
            models.Index(fields=['topic'], name='topic_idx'),
            models.Index(fields=['event_timestamp'], name='event_timestamp_idx'),
        ]
