"""**** Scripted by Antony Silvester ****** """
import json
from urllib import addbase
import os


import requests
from requests.auth import HTTPBasicAuth


class BgpLs:

    def __init__(self):
        self.localAs = 100
        self.maxSession = 20
        self.lsCapability = True
        self.holdTime = 180
        self.largeAsCapability = False
        self.flowSpecCapability = 'IPV4'
        self.flowSpecRpdCapability = False
        self.remoteAs = 100
        self.peerHoldTime = 120
        self.connectMode = 'active'
        self.bgpPeer = []
        self.routerId = ''
        self.peerIp = ''
        #self.org_bgp = []

    def ipValue(self,localip,remoteip):
        self.routerId = localip
        self.peerIp = remoteip
        return self.routerId , self.peerIp

    def DictoJson(self):
        Dicdata = {}
        org_bgp =[]
        org_bgp.append({'peerIp': self.peerIp , 'remoteAs':self.remoteAs,
                        'peerHoldTime':self.peerHoldTime , 'connectMode':self.connectMode })
        if self.routerId != '':
            Dicdata['routerId'] = self.routerId
        if self.localAs != '':
            Dicdata['localAs'] = self.localAs
        if self.maxSession != '':
            Dicdata['maxSession'] = self.maxSession
        if self.lsCapability != '':
            Dicdata['lsCapability'] = self.lsCapability
        if self.holdTime != '':
            Dicdata['holdTime'] = self.holdTime
        if self.largeAsCapability != '':
            Dicdata['largeAsCapability'] = self.largeAsCapability
        if self.flowSpecCapability != '':
            Dicdata['flowSpecCapability'] = self.flowSpecCapability
        if self.flowSpecRpdCapability != '':
            Dicdata['flowSpecRpdCapability'] = self.flowSpecRpdCapability
        if self.bgpPeer != '':
            Dicdata['bgpPeer'] = org_bgp

        Dicdata = {'bgpapp':Dicdata}
        Dicdata = {'org.onosproject.provider.bgp.cfg':Dicdata}
        Dicdata = {'apps':Dicdata}
        return json.dumps(Dicdata,indent=4)


    def  Comments(self):
        print("**********************************************************************************\n")

    def Constants(self):
        self.Ne_id_1 =  '1111.1111.0011'
        self.Ne_id_2 = '2222.2222.0022'
        self.Ne_id_3 = '3333.3333.0033'
        self.Ne_id_4 = '4444.4444.0044'
        listnum = [self.Ne_id_1,self.Ne_id_2,self.Ne_id_3,self.Ne_id_4,]
        var = [self.peerIp]
        return var,listnum

    def apps(self):
        self.app_bgp = 'org.onosproject.bgp'
        self.app_bgpflow = 'org.onosproject.bgpflow'
        self.list1 = [self.app_bgp,self.app_bgpflow]
        return self.list1
