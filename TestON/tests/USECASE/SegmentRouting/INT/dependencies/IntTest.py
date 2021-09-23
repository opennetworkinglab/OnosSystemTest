# SPDX-FileCopyrightText: Copyright 2021-present Open Networking Foundation.
# SPDX-License-Identifier: GPL-2.0-or-later

from tests.dependencies.Network import Network

class IntTest:

    def __init__(self, scapy=False):
        self.hosts = ["h1", "h2", "h3"]
        self.scapy = scapy

    def setUpTest(self, main):
        main.Network = Network()
        main.Network.connectToNet()

        for host in self.hosts:
            main.Network.createHostComponent(host)
            if self.scapy:
                hostHandle = getattr(main, host)
                hostHandle.sudoRequired = True
                hostHandle.startScapy()

    def cleanUp(self, main):
        for host in self.hosts:
            if self.scapy:
                hostHandle = getattr(main, host)
                hostHandle.stopScapy()
            main.Network.removeHostComponent(host)
        main.Network.disconnectFromNet()
