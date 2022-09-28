FROM ubuntu:20.04

# Metadata
LABEL MAINTAINER="luciano@citrait.com.br"

# TZ
ENV PATH="/scripts:${PATH}"
ENV TZ America/Sao_Paulo
RUN echo $TZ > /etc/timezone


# Atualizando a lista de pacotes
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -y update >/dev/null \
	&& apt-get -y dist-upgrade >/dev/null \
	&& apt-get -y install --no-install-recommends \
		python3.8 \
		python3-pip \
		python3-psycopg2 \
		python3.8-dev \
		build-essential >/dev/null 2>&1


# Installing Python Requirements
COPY src/pfsense_portal/requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt >/dev/null


# gunicorn WSGI
RUN python3.8 -m pip install gunicorn


# Cleanup package cache data
RUN rm -rf /var/lib/apt/lists/*


# Adjusting ssl weak cipher acceptance
COPY ssl/openssl.cnf /etc/ssl/openssl.cnf

# Copiando os arquivos da aplicação
RUN mkdir /app
RUN mkdir /scripts
COPY scripts/ /scripts
COPY src/pfsense_portal/ /app
WORKDIR /app


# Expondo a porta 80
EXPOSE 80
EXPOSE 5000-5100


# Default Entrypoint
RUN chmod +x /scripts/entrypoint.sh
CMD ["/scripts/entrypoint.sh"]