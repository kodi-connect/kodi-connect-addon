FROM python:2.7

ENV HOME=/home/python

RUN apt-get update && \
  apt-get install -y \
    zip && \
  useradd -m python && \
  mkdir -p $HOME/app && \
  chown -R python:python $HOME/app

WORKDIR $HOME/app

USER python

RUN bash
