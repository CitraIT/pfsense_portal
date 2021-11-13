FROM ubuntu:20.04

# Metadata
LABEL MAINTAINER="luciano@citrait.com.br"

# TZ
ENV PATH="/scripts:${PATH}"
ENV TZ America/Sao_Paulo
RUN echo $TZ > /etc/timezone


# Atualizando a lista de pacotes
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -y update \
        && apt-get -y dist-upgrade \
        && apt-get -y install --no-install-recommends \
                python3.8 \
                python3-pip \
                python3-psycopg2 \
        python3.8-dev \
        build-essential \
                cron \
                iputils-ping \
                net-tools \
                dnsutils 

# CRON SETUP
RUN mkdir -p /var/spool/cron/crontabs
COPY crontabs/root /var/spool/cron/crontabs/root
RUN chmod 0644 /var/spool/cron/crontabs/root
RUN /usr/bin/crontab /var/spool/cron/crontabs/root


# Installing Python Requirements
COPY src/pfsense_portal/requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt


# gunicorn WSGI
# RUN python3.8 -m pip install gunicorn


# Cleanup package cache data
RUN rm -rf /var/lib/apt/lists/*


# Copiando os arquivos da aplicação
RUN mkdir /app
RUN mkdir /scripts
COPY scripts/ /scripts
COPY src/pfsense_portal/ /app
WORKDIR /app

# Executable files
# RUN chmod +x /scripts/*
# RUN chmod +x /app/backup_runner.py


# Expondo a porta 8000
EXPOSE 80


# Definindo o gunicorn como ponto de entrada
# ENTRYPOINT [ "gunicorn", "--workers=5", "--threads=2", "--worker-class=gthread","--bind", "0.0.0.0:80", "--worker-tmp-dir","/dev/shm", "core.wsgi"]
#ENTRYPOINT [ "python3.8", "app.py"]
VOLUME /app

# Default Entrypoint
chmod +x /scripts/entrypoint.sh
CMD ["/scripts/entrypoint.sh"]