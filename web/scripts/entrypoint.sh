#!/bin/bash
set -e

# Starting cron
/usr/sbin/cron
/usr/bin/crontab /var/spool/cron/crontabs/root

# Creating needed directories
mkdir -p /app/files/backup


# python3 manage.py collectstatic --noinput
python3 manage.py makemigrations
python3 manage.py migrate
# python3 manage.py runserver 0.0.0.0:80

# uwsgi --socket :80 --master --enable-threads  --plugin=python38 --module core.wsgi
/usr/local/bin/gunicorn --workers=2 \
    --threads=2 \
    --worker-class=gthread \
    --bind 0.0.0.0:80 \
    --worker-tmp-dir /dev/shm core.wsgi \
    --access-logfile - 

