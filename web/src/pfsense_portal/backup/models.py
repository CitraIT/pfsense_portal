import os
import sys
from pathlib import Path
import requests
import re
from django.db import models
from django.utils import timezone
from firewall.models import Firewall


#
BACKUP_RECURRENCE = [
    ('DAILY', 'daily'),
    ('HOURLY', 'hourly'),
    ('WEEKLY', 'weekly'),
    ('MONTLY', 'montly')
]

#
#
#
class BackupFile(models.Model):
    path         = models.CharField(max_length=255)
    is_encrypted = models.BooleanField(default=False)
    

#
#
#
class Backup(models.Model):
    firewall    = models.ForeignKey(Firewall, null=True, blank=True, on_delete=models.CASCADE)
    start_date  = models.DateTimeField(default=timezone.now)
    finish_date = models.DateTimeField()
    file        = models.ForeignKey(BackupFile, null=True, blank=True, on_delete=models.CASCADE)


#
#
#
class BackupPolicy(models.Model):
    name        = models.CharField(max_length=40, default='default policy')
    run_hour    = models.IntegerField(default=20)
    run_minute = models.IntegerField(default=0)
    run_cycle   = models.CharField(max_length=10, choices=BACKUP_RECURRENCE, default='daily')
    last_run    = models.DateTimeField(null=True, blank=True)



