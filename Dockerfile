FROM ubuntu:17.10

RUN apt-get update -y &&\
    apt-get install -y \
            git \
            make \
            python \
            python-pip \
            zip

RUN git clone https://github.com/initbar/sipd /srv &&\
    cd /srv/sipd &&\
    make

WORKDIR /root

CMD ["/srv/sipd/sipd"]
