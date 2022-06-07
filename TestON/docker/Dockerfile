# SPDX-FileCopyrightText: Copyright 2021-present Open Networking Foundation.
# SPDX-License-Identifier: Apache-2.0
ARG SCAPY_VER=2.4.5
ARG TREX_VER=3532cf99daf6dd3a1a284d0f1c388f1773eadc8a
ARG TREX_EXT_LIBS=/external_libs
ARG TREX_LIBS=/trex_python
ARG KUBECTL=v1.22.1
ARG ONOS_VER=2.5.4
ARG RANCHER_VER=2.6.5
ARG GO_VER=1.18.2
ARG TFMASK_VER=0.7.0

# Install TRex deps
FROM alpine:3.12.1 as trex-builder
ARG TREX_VER
ARG TREX_EXT_LIBS
ARG TREX_LIBS
# Install Trex library
ENV TREX_SCRIPT_DIR=/trex-core-${TREX_VER}/scripts
RUN wget https://github.com/stratum/trex-core/archive/${TREX_VER}.zip
RUN unzip -qq ${TREX_VER}.zip && \
    mkdir -p /output/${TREX_EXT_LIBS} && \
    mkdir -p /output/${TREX_LIBS} && \
    cp -r ${TREX_SCRIPT_DIR}/automation/trex_control_plane/interactive/* /output/${TREX_LIBS} && \
    cp -r ${TREX_SCRIPT_DIR}/external_libs/* /output/${TREX_EXT_LIBS} && \
    cp -r ${TREX_SCRIPT_DIR}/automation/trex_control_plane/stf/trex_stf_lib /output/${TREX_LIBS}

FROM ubuntu:20.04
ARG TREX_EXT_LIBS
ARG TREX_LIBS
ARG SCAPY_VER
ARG KUBECTL
ARG JENKINS_URL
ARG JENKINS_NODE
ARG ONOS_VER
ARG RANCHER_VER
ARG GO_VER
ARG TFMASK_VER
ENV DEBIAN_FRONTEND=noninteractive
ENV PACKAGES \
    python \
    python3 \
    python3-pip \
    ssh \
    openssh-server \
    curl \
    supervisor \
    git \
    iproute2 \
    openjdk-11-jre \
    software-properties-common \
    git-crypt \
    gnupg-agent \
    sudo
ADD requirements.txt /

COPY --from=trex-builder /output /

RUN apt update && \
    apt install --no-install-recommends -y $PACKAGES && \
    curl -L "https://dl.k8s.io/release/$KUBECTL/bin/linux/amd64/kubectl" -o /usr/local/bin/kubectl && \
    chmod 0755 /usr/local/bin/kubectl && \
    curl https://bootstrap.pypa.io/pip/2.7/get-pip.py | python && \
    python -m pip install setuptools && \
    python -m pip install -r  requirements.txt && \
    python3 -m pip install p4runtime-shell==0.0.2 && \
    cd ${TREX_EXT_LIBS}/scapy-${SCAPY_VER} && python setup.py install && \
    mkdir -p /var/run/sshd && \
    mkdir -p /var/log/supervisor && \
    useradd -m jenkins -G sudo && \
    chmod 777 /tmp && \
    chsh -s /bin/bash jenkins && \
    echo jenkins:jenkins | chpasswd

ARG ENV

RUN if [ "$ENV" = "linux" ] ; then groupmod --gid 1001 jenkins && usermod --uid 1001 jenkins ; fi

RUN curl -sS --fail "https://repo1.maven.org/maven2/org/onosproject/onos-releases/${ONOS_VER}/onos-admin-${ONOS_VER}.tar.gz" | tar zx && \
    mv onos-admin-${ONOS_VER}/* /usr/local/bin/ && \
    rm -r onos-admin-${ONOS_VER}

RUN curl -L -sS --fail "https://github.com/rancher/cli/releases/download/v${RANCHER_VER}/rancher-linux-amd64-v${RANCHER_VER}.tar.gz" | tar zx && \
    mv rancher-v${RANCHER_VER}/rancher /usr/local/bin && \
    rm -r rancher-v${RANCHER_VER}

RUN cd /usr/local && curl -L -sS --fail https://go.dev/dl/go${GO_VER}.linux-amd64.tar.gz | tar zx
ENV PATH=$PATH:/usr/local/go/bin

RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add - && \
    apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main" && \
    apt-get update && apt-get install terraform

RUN curl -Lo /usr/local/bin/tfmask https://github.com/cloudposse/tfmask/releases/download/${TFMASK_VER}/tfmask_linux_amd64 && \
    chmod +x /usr/local/bin/tfmask 
RUN ln -s /trex_python /home/jenkins/trex_python
RUN echo '%jenkins ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV PYTHONPATH=${TREX_EXT_LIBS}:${TREX_LIBS}
# TODO: should we parametrize those?
ENV OC1=localhost
ENV OC2=localhost
ENV OC3=localhost
ADD docker/fs /
RUN chown -R jenkins.jenkins /home/jenkins && \
    python -m pip install -r /tmp/additional-py-pkgs.txt && \
    chmod 1777 /tmp
ENV JENKINS_URL=${JENKINS_URL}
ENV JENKINS_NODE=${JENKINS_NODE}

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]

EXPOSE 22
