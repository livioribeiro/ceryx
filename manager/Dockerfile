# FROM python:3.6.1-alpine
# MAINTAINER Livio Ribeiro <livioribeiro@outlook.com>

# RUN mkdir -p /opt/ceryx
# WORKDIR /opt/ceryx

# COPY requirements.txt /opt/ceryx/requirements.txt
# RUN pip install -r requirements.txt

# COPY . /opt/ceryx

# CMD gunicorn -b 0.0.0.0:80 ceryx.manager:app



FROM python:3.6.1-alpine
MAINTAINER Livio Ribeiro <livioribeiro@outlook.com>

COPY . /opt/ceryx
WORKDIR /opt/ceryx
RUN pip install /opt/ceryx

CMD gunicorn -b 0.0.0.0:80 ceryx.manager:app
