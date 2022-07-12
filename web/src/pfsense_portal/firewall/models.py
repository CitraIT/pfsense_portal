import os
import requests
import re
from pathlib import Path
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE
from django.utils.timezone import now

# Create your models here.
class Firewall(models.Model):
    # customer = ForeignKey('Customer', on_delete=CASCADE)
    name = models.CharField(max_length=20)
    last_seen = models.DateTimeField(blank=True, null=True)
    api_key = models.CharField(max_length=32, blank=True)
    is_online = models.BooleanField(default=False)
    user_reverse_port = models.IntegerField(blank=True, null=True)
    control_channel_port = models.IntegerField(blank=True, null=True)


    def __str__(self):
        return self.name




