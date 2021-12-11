import os
import sys
import logging
import datetime
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
# from django.utils.timezone import  now
from datetime import datetime
from backup.models import Backup, BackupPolicy, BackupFile
from firewall.models import Firewall
from firewall.firewalls import PFSense


# Basic Logging
def log_event(message, raw=False):
    f = open("/var/log/scheduled_tasks_runner.log", 'a')
    if raw:
        f.write(message + '\n')
    else:
        log_prefix = datetime.now().strftime('%Y-%m-%d %H:%M:%S: ')
        f.write(f'{log_prefix} {message}\n')
    f.close()

# logging setup
# consoleHandler = logging.StreamHandler()
# log_format = "%(asctime)s %(levelname)-8s %(name)-10s: %(message)s"
# logging.basicConfig(level=logging.DEBUG, format=log_format)
# consoleHandler.setFormatter(logging.Formatter(log_format))
# consoleHandler.setLevel(logging.DEBUG)
# log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)
# log.addHandler(consoleHandler)
# log.debug('logging setup')






# Evaluate if there are any backups to run
# log_event("Starting scheduled tasks runner script")
right_now = datetime.now()
for policy in BackupPolicy.objects.all():
    #
    seconds_to_next_run = 0
    
    # # calculate the next run for this policy
    # if policy.run_cycle == 'daily':
    #     seconds_to_next_run = 24 * 60 * 60
    # elif policy.run_cycle == 'hourly':
    #     seconds_to_next_run = 60 * 60
    
    # # evaluate if it's time to run a backup task
    # seconds_synce_last_run = int( now().timestamp() - policy.last_run.timestamp() )
    # if seconds_to_next_run < seconds_synce_last_run :
    ## COMMENTED, SO WE COULD NOT RELIABLE YET CALCULATE EXACLTY LAST RUN WITH SCHEDULE IF THE USER RUN THE TASK MANUALLY
    if policy.run_hour == right_now.hour and policy.run_minute == right_now.minute:
        # The backup policy is timedout, run it now
        log_event(f'starting a new task for backup policy: {policy.name}')
        for firewall in Firewall.objects.all():
            log_event(f'backuping up firewall: {firewall.name}')
            backup = Backup(firewall=firewall, start_date=right_now)
            pfsense =  PFSense(url=firewall.url, username=firewall.admin_user, password=firewall.admin_pass)
            pfsense.get_landing_page()
            pfsense.login()
            backup.file = BackupFile(path=pfsense.backup_config())
            backup.file.save()
            backup.finish_date = datetime.now()
            backup.save()
        log_event(f'finished a task for backup policy: {policy.name}')
        policy.last_run = datetime.now()
        policy.save()
    else:
        log_event(f'backup policy {policy.name} not ready to run. it will run at {policy.run_hour}:{policy.run_minute}')

# log_event("Ending scheduled tasks runner script")

