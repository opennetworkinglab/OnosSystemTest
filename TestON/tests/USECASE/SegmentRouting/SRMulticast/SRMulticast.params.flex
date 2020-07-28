<PARAMS>
    <testcases>1,2,4</testcases>

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
        <confName>flex</confName>
        <topology>hagg_fabric.py</topology>
        <lib>routinglib.py,trellislib.py</lib>
        <conf>bgpdbgp1.conf,bgpdbgp2.conf,bgpdr1.conf,bgpdr2.conf,dhcpd6.conf,dhcpd.conf,zebradbgp1.conf,zebradbgp2.conf</conf>
        <trellisOar>/home/sdn/segmentrouting-oar-3.0.0-SNAPSHOT.oar</trellisOar>
        <t3Oar>/home/sdn/t3-app-3.0.0-SNAPSHOT.oar</t3Oar>
    </DEPENDENCY>

    <ENV>
        <cellName>productionCell</cellName>
        <cellApps>drivers,openflow,fpm,dhcprelay,netcfghostprovider,routeradvertisement,mcast,hostprobingprovider</cellApps>
    </ENV>

    <GIT>
        <pull>False</pull>
        <branch>master</branch>
    </GIT>

    <ONOS_Configuration>
    </ONOS_Configuration>

    <ONOS_Logging>
        <org.onosproject.events>TRACE</org.onosproject.events>
        <org.onosproject.segmentrouting>DEBUG</org.onosproject.segmentrouting>
        <org.onosproject.driver>DEBUG</org.onosproject.driver>
        <org.onosproject.net.flowobjective.impl>DEBUG</org.onosproject.net.flowobjective.impl>
        <org.onosproject.routeservice.impl>DEBUG</org.onosproject.routeservice.impl>
        <org.onosproject.routeservice.store>DEBUG</org.onosproject.routeservice.store>
        <org.onosproject.routing.fpm>DEBUG</org.onosproject.routing.fpm>
        <org.onosproject.fpm>DEBUG</org.onosproject.fpm>
        <org.onosproject.mcast>DEBUG</org.onosproject.mcast>
    </ONOS_Logging>


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
        <HOSTNAMES>h1,h2,h3,h4</HOSTNAMES>
    </SCAPY>

    <TOPO>
        <switchNum>10</switchNum>
        <linkNum>48</linkNum>
    </TOPO>

</PARAMS>
