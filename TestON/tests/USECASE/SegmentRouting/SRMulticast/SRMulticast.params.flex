<PARAMS>
    <testcases>1,1</testcases>

    <GRAPH>
        <nodeCluster>Fabric</nodeCluster>
        <builds>20</builds>
    </GRAPH>

    <SCALE>
        <size>3</size>
        <max>3</max>
    </SCALE>

    <DEPENDENCY>
        <useCommonConf>False</useCommonConf>
        <useCommonTopo>True</useCommonTopo>
        <topology>hagg_fabric.py</topology>
        <lib>routinglib.py,trellislib.py</lib>
        <conf>bgpdbgp1.conf,bgpdbgp2.conf,bgpdr1.conf,bgpdr2.conf,dhcpd6.conf,dhcpd.conf,zebradbgp1.conf,zebradbgp2.conf</conf>
    </DEPENDENCY>

    <ENV>
        <cellName>productionCell</cellName>
        <cellApps>drivers,segmentrouting,openflow,fpm,dhcprelay,netcfghostprovider,routeradvertisement,t3,mcast,hostprobingprovider</cellApps>
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
        <OnosDiscovery>30</OnosDiscovery>
        <loadNetcfgSleep>5</loadNetcfgSleep>
        <connectToNetSleep>30</connectToNetSleep>
        <balanceMasterSleep>10</balanceMasterSleep>
        <mcastSleep>5</mcastSleep>
    </timers>

    <RETRY>
        <hostDiscovery>10</hostDiscovery>
    </RETRY>

    <SCAPY>
        <HOSTNAMES>h1,h2</HOSTNAMES>
    </SCAPY>

    <TOPO>
        <switchNum>10</switchNum>
        <linkNum>48</linkNum>
    </TOPO>

</PARAMS>
