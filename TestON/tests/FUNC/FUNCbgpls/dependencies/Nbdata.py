"**** Scripted by Antony Silvester ****** "
import json
from urllib import addbase
import os


import requests
from requests.auth import HTTPBasicAuth


class BgpLs:

    def __init__( self ):
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

    def ipValue( self, localip, remoteip ):
        self.routerId = localip
        self.peerIp = remoteip
        return self.routerId, self.peerIp

    def DictoJson( self ):
        Dicdata = {}
        org_bgp = []
        org_bgp.append( { 'peerIp': self.peerIp, 'remoteAs': self.remoteAs,
                          'peerHoldTime': self.peerHoldTime, 'connectMode': self.connectMode } )
        if self.routerId != '':
            Dicdata[ 'routerId' ] = self.routerId
        if self.localAs != '':
            Dicdata[ 'localAs' ] = self.localAs
        if self.maxSession != '':
            Dicdata[ 'maxSession' ] = self.maxSession
        if self.lsCapability != '':
            Dicdata[ 'lsCapability' ] = self.lsCapability
        if self.holdTime != '':
            Dicdata[ 'holdTime' ] = self.holdTime
        if self.largeAsCapability != '':
            Dicdata[ 'largeAsCapability' ] = self.largeAsCapability
        if self.flowSpecCapability != '':
            Dicdata[ 'flowSpecCapability' ] = self.flowSpecCapability
        if self.flowSpecRpdCapability != '':
            Dicdata[ 'flowSpecRpdCapability' ] = self.flowSpecRpdCapability
        if self.bgpPeer != '':
            Dicdata[ 'bgpPeer' ] = org_bgp

        Dicdata = { 'bgpapp': Dicdata }
        Dicdata = { 'org.onosproject.provider.bgp.cfg': Dicdata }
        Dicdata = { 'apps': Dicdata }
        return json.dumps( Dicdata, indent=4 )

    def Comments( self ):
        print( "**********************************************************************************\n" )

    def Constants( self ):
        self.Ne_id_1 = '1111.1111.0011'
        self.Ne_id_2 = '2222.2222.0022'
        self.Ne_id_3 = '3333.3333.0033'
        self.Ne_id_4 = '4444.4444.0044'
        listnum = [ self.Ne_id_1, self.Ne_id_2, self.Ne_id_3, self.Ne_id_4, ]
        var = [ self.peerIp ]
        return var, listnum

    def apps( self ):
        self.app_bgp = 'org.onosproject.bgp'
        self.app_bgpflow = 'org.onosproject.bgpflow'
        self.list1 = [ self.app_bgp, self.app_bgpflow ]
        return self.list1

    def checkLinks( self, linksResp ):
        # Declaring the links values
        links = { 'link1_src': "1650.5555.0055", 'link1_dst': "1660.6666.0066",
                  'link2_src': "1630.3333.0033", 'link2_dst': "1620.2222.0022",
                  'link3_src': "1660.6666.0066", 'link3_dst': "1650.5555.0055",
                  'link4_src': "1630.3333.0033", 'link4_dst': "1650.5555.0055",
                  'link5_src': "1640.4444.0044", 'link5_dst': "1610.1111.0011",
                  'link6_src': "1650.5555.0055", 'link4_dst': "1630.3333.0033",
                  'link7_src': "1620.2222.0022", 'link4_dst': "1630.3333.0033",
                  'link8_src': "1620.2222.0022", 'link4_dst': "1610.1111.0011",
                  'link9_src': "1630.3333.0033", 'link4_dst': "1640.4444.0044",
                  'link10_src': "1650.5555.0055", 'link4_dst': "1640.4444.0044",
                  'link11_src': "1610.1111.0011", 'link4_dst': "1640.4444.0044",
                  'link12_src': "1640.4444.0044", 'link4_dst': "1620.2222.0022",
                  'link13_src': "1660.6666.0066", 'link4_dst': "1630.3333.0033",
                  'link14_src': "1640.4444.0044", 'link4_dst': "1660.6666.0066",
                  'link15_src': "1640.4444.0044", 'link4_dst': "1630.3333.0033",
                  'link16_src': "1610.1111.0011", 'link4_dst': "1630.3333.0033",
                  'link17_src': "1630.3333.0033", 'link4_dst': "1610.1111.0011",
                  'link18_src': "1610.1111.0011", 'link4_dst': "1620.2222.0022",
                  'link19_src': "1620.2222.0022", 'link4_dst': "1640.4444.0044",
                  'link20_src': "1630.3333.0033", 'link4_dst': "1660.6666.0066",
                  'link21_src': "1640.4444.0044", 'link4_dst': "1650.5555.0055",
                  'link22_src': "1660.6666.0066", 'link4_dst': "1640.4444.0044"
                  }

        # Comparing the Links
        for x in xrange( 22 ):
            link_src_info = linksResp[ x ][ 'src' ][ 'device' ]
            link_dst_info = linksResp[ x ][ 'dst' ][ 'device' ]
            link_src_split = link_src_info.split( "=" )
            link_src = link_src_split[ 4 ]
            link_dst_split = link_dst_info.split( "=" )
            link_dst = link_dst_split[ 4 ]
            y = x + 1
            link_src_ref = links[ 'link' + str( y ) + '_src' ]
            link_dst_ref = links[ 'link' + str( y ) + '_dst' ]
            if ( link_src == link_src_ref ) and ( link_dst == ( link_dst_ref ) and
                                                   linksResp[ x ][ 'type' ] == 'DIRECT' and linksResp[ x ][ 'state' ] ==
                                                  'ACTIVE' ):
                return True
            else:
                return False
