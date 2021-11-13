import os
from pathlib import Path
from django.contrib.auth import login
from django.http.response import Http404
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Backup, BackupFile, BackupPolicy
from firewall.models import Firewall
from firewall.firewalls import PFSense
from datetime import datetime



@login_required
def index(request):
    try:
        policy = BackupPolicy.objects.get(id=1)
    except BackupPolicy.DoesNotExist:
        policy = BackupPolicy(name='default policy', run_hour=20, run_minutes=00)
        policy.save()
    
    backups = Backup.objects.order_by("-start_date")[:30]
    return render(request, 'backup/index.html', context={'policies': [policy, ], 'backups':backups})


@login_required
def run_backup(request, policy_id):
    firewalls = Firewall.objects.all()
    for firewall in firewalls:
        now = datetime.now()
        backup = Backup(firewall=firewall, start_date=now)
        pfsense =  PFSense(url=firewall.url, username=firewall.admin_user, password=firewall.admin_pass)
        pfsense.get_landing_page()
        pfsense.login()
        backup.file = BackupFile(path=pfsense.backup_config())
        backup.file.save()
        backup.finish_date = datetime.now()
        backup.save()
    return HttpResponse(f"Finished all backups!")



@login_required
def download_backup(request, backup_id):
    try:
        backup = Backup.objects.get(id=backup_id)
        return FileResponse(open(backup.file.path, "rb"), as_attachment=True)
    except Backup.DoesNotExist:
        return Http404()
