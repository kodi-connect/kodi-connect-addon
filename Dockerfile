FROM python:2.7

ENV HOME=/home/python

RUN apt-get update && \
  apt-get install -y zip && \
  pip install pylint flake8 ipdb && \
  touch /usr/bin/cec-client && chmod +x /usr/bin/cec-client && \
  useradd -m python && \
  mkdir -p $HOME/app && \
  chown -R python:python $HOME

WORKDIR $HOME/app

USER python

RUN bash
