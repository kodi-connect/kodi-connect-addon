# FROM python:2.7
FROM python:3.6

ENV HOME=/home/python

RUN apt-get --allow-releaseinfo-change update && \
  apt-get install -y zip && \
  pip install pylint flake8 ipdb && \
  touch /usr/bin/cec-client && chmod +x /usr/bin/cec-client && \
  useradd -m python && \
  mkdir -p $HOME/app && \
  chown -R python:python $HOME

# Virtualenv
RUN pip install virtualenv

# Kodi dependencies
RUN pip install future==0.17.1

# Development dependencies
RUN pip install mypy black pylint flake8

WORKDIR $HOME/app

USER python

RUN bash
