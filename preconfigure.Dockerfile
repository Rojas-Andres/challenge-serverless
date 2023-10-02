FROM python:3.9-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
    gcc g++ libxml2-dev libxslt-dev libssl-dev make \
    libpq-dev postgis \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY layer_dependencies_basic/ /usr/src/app/layer_dependencies_basic/
COPY local.txt /usr/src/app/

WORKDIR /usr/src/app/

RUN pip install --no-cache-dir -r local.txt