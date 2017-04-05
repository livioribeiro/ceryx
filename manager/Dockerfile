FROM python:3.6.1-alpine
MAINTAINER Livio Ribeiro <livioribeiro@outlook.com>

RUN apk add --update build-base libffi-dev postgresql-dev
RUN apk add libffi libpq

COPY requirements.txt /opt/ceryx/requirements.txt
RUN pip install -r /opt/ceryx/requirements.txt

RUN apk del build-base libffi-dev postgresql-dev

COPY . /opt/ceryx
WORKDIR /opt/ceryx

CMD gunicorn -b 0.0.0.0:80 ceryx.manager:app
