FROM opennetworking/mn-stratum

ENV HOME /home/root
WORKDIR $HOME
RUN ln -s /root/* .
RUN chmod 777 $HOME

RUN install_packages python-pip openvswitch-switch vim quagga isc-dhcp-server isc-dhcp-client iptables vlan
RUN pip install ipaddress

RUN ln -s $HOME /var/run/quagga
RUN ln -s /usr/sbin/zebra /usr/lib/quagga/zebra
RUN ln -s /usr/sbin/bgpd /usr/lib/quagga/bgpd

# try to ensure dhclient can write pid files
RUN chmod 777 /run
RUN ls -al $HOME
# Issue with Uubuntu/Apparmour
RUN mv /sbin/dhclient /usr/local/bin/ \
&& touch /var/lib/dhcp/dhcpd.leases

# Install custom mininet branch
run install_packages git sudo lsb-release
RUN git clone https://github.com/jhall11/mininet.git \
&& cd mininet \
&& git branch -v -a \
&& git checkout -b dynamic_topo origin/dynamic_topo \
&& cd util \
&& alias sudo='' \
&& apt-get update \
&& ./install.sh -3fvn
ENTRYPOINT bash
