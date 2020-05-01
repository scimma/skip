from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.


class Target(models.Model):
    name = models.CharField(max_length=200)


class Event(models.Model):
    target_id = models.ForeignKey(Target, on_delete=models.CASCADE)
    message = JSONField()
