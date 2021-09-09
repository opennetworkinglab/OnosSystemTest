# SPDX-FileCopyrightText: Copyright 2021-present Open Networking Foundation.
# SPDX-License-Identifier: Apache-2.0
FROM ubuntu:18.04

ARG KUBECTL=v1.22.1
ENV PACKAGES \
    python \
    python-pip \
    ssh \
    openssh-server \
    curl \
    supervisor
ADD requirements.txt /

RUN apt update && \
    apt install --no-install-recommends -y $PACKAGES && \
    curl -L "https://dl.k8s.io/release/$KUBECTL/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl && \
    chmod 0755 /usr/local/bin/kubectl && \
    python -m pip install setuptools && \
    python -m pip install -r requirements.txt && \
    mkdir -p /var/run/sshd && \
    mkdir -p /var/log/supervisor && \
    useradd -m jenkins && \
    chsh -s /bin/bash jenkins && \
    echo jenkins:jenkins | chpasswd

ADD docker/fs /
RUN chown -R jenkins.jenkins /home/jenkins && \
    python -m pip install -r /tmp/additional-py-pkgs.txt

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]

EXPOSE 22
