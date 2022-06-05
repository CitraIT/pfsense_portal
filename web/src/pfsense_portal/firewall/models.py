import os
import requests
import re
from pathlib import Path
from django.db import models


# Create your models here.
class Firewall(models.Model):
    name = models.CharField(max_length=20)
    url = models.URLField(max_length=100, blank=False, null=False)
    admin_user = models.CharField(max_length=20)
    admin_pass = models.CharField(max_length=40)
    api_key = models.CharField(max_length=32, blank=True)
    is_online = models.BooleanField(default=False)
    user_reverse_port = models.IntegerField(blank=True, null=True)


    def __str__(self):
        return self.name




