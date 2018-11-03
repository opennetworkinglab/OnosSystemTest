<PARAMS>
    <testcases>1</testcases>

    <GRAPH>
        <nodeCluster>Fabric</nodeCluster>
        <builds>20</builds>
    </GRAPH>

    <SCALE>
        <size>7</size>
        <max>7</max>
    </SCALE>

    <DEPENDENCY>
        <useCommonConf>False</useCommonConf>
        <useCommonTopo>True</useCommonTopo>
        <confName>flex</confName>
        <topology>hagg_fabric.py</topology>
        <lib>routinglib.py,trellislib.py,trellis_fabric.py</lib>
        <conf>bgpdbgp1.conf,bgpdbgp2.conf,bgpdr1.conf,bgpdr2.conf,dhcpd6.conf,dhcpd.conf,zebradbgp1.conf,zebradbgp2.conf</conf>
    </DEPENDENCY>

    <ENV>
        <cellName>productionCell</cellName>
        <cellApps>drivers,openflow,segmentrouting,fpm,dhcprelay,netcfghostprovider,routeradvertisement,t3,hostprobingprovider</cellApps>
    </ENV>

    <GIT>
        <pull>False</pull>
        <branch>master</branch>
    </GIT>

    <CTRL>
        <port>6653</port>
    </CTRL>

    <timers>
        <LinkDiscovery>30</LinkDiscovery>
        <SwitchDiscovery>30</SwitchDiscovery>
        <OnosDiscovery>45</OnosDiscovery>
        <loadNetcfgSleep>5</loadNetcfgSleep>
        <startMininetSleep>25</startMininetSleep>
        <dhcpSleep>60</dhcpSleep>
        <balanceMasterSleep>10</balanceMasterSleep>
        <connectToNetSleep>30</connectToNetSleep>
    </timers>

    <TOPO>
        <internalIpv4Hosts>h4v4,h5v4,h9v4,h10v4</internalIpv4Hosts>
        <internalIpv6Hosts>h4v6,h5v6,h9v6,h10v6</internalIpv6Hosts>
        <externalIpv4Hosts></externalIpv4Hosts>
        <externalIpv6Hosts></externalIpv6Hosts>
        <staticIpv4Hosts></staticIpv4Hosts>
        <staticIpv6Hosts></staticIpv6Hosts>
        <switchNum>10</switchNum>
        <linkNum>48</linkNum>
    </TOPO>

</PARAMS>
