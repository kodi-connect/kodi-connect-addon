FROM phusion/baseimage:0.9.22
LABEL Author Tomas Kislan <kislan.tomas@gmail.com>

ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV TZ=Europe/Zurich
ENV SCREEN_RESOLUTION 1024x768
ENV DISPLAY :0

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN add-apt-repository ppa:team-xbmc/ppa && \
  apt-get update && \
  apt-get -y install \
    git-core \
    git \
    net-tools \
    xvfb \
    x11vnc \
    supervisor \
    fluxbox \
    kodi

RUN apt-get autoclean

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /root/

EXPOSE 8080 5900

CMD ["/usr/bin/supervisord"]
