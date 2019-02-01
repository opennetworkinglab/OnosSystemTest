<PARAMS>
    # 0. Initialize CHOTestMonkey
    # 1. Set IPv6 configure
    # 2. Load network configuration files
    # 4. Copy topology libs and config files to Mininet
    # 5. Load topology and balances all switches
    # 6. Collect and store device and link data from ONOS
    # 7. Collect and store host data from ONOS
    # 10. Run all enabled checks
    # 70. Run randomly generated events
    # 80. Replay events from log file
    # 100. Do nothing

    <testcases>
        0,2,5,6,7,10,70
    </testcases>

    <GIT>
        <pull>False</pull>
        <branch>master</branch>
    </GIT>

    <TEST>
        <IPv6>off</IPv6>
        <restartCluster>False</restartCluster>
        <dataPlaneConnectivity>True</dataPlaneConnectivity>
        <numCtrl>3</numCtrl>
        <pauseTest>on</pauseTest>
        <caseSleep>0</caseSleep>
        <ipv6Regex>10[0-9]+::[0-9]+</ipv6Regex>
        <ipv4Regex>10\.0\.[0-9]+\.[0-9]+</ipv4Regex>
        <karafCliTimeout>7200000</karafCliTimeout>
        <testDuration>86400</testDuration>
        <package>on</package>
    </TEST>

    <GRAPH>
        <nodeCluster>CHO</nodeCluster>
        <builds>20</builds>
    </GRAPH>

    <ENV>
        <cellName>choFlexCell</cellName>
        <cellApps>drivers,openflow,segmentrouting,fpm,dhcprelay,netcfghostprovider,routeradvertisement,t3,hostprobingprovider</cellApps>
    </ENV>

    <EVENT>
        <Event>
            <status>on</status>
            <typeIndex>0</typeIndex>
            <typeString>NULL</typeString>
            <CLI>null</CLI>
            <CLIParamNum>0</CLIParamNum>
            <rerunInterval>5</rerunInterval>
            <maxRerunNum>3</maxRerunNum>
        </Event>

        <TestPause>
            <status>on</status>
            <typeIndex>1</typeIndex>
            <typeString>TEST_PAUSE</typeString>
            <CLI>pause-test</CLI>
            <CLIParamNum>0</CLIParamNum>
        </TestPause>

        <TestResume>
            <status>on</status>
            <typeIndex>2</typeIndex>
            <typeString>TEST_RESUME</typeString>
            <CLI>resume-test</CLI>
            <CLIParamNum>0</CLIParamNum>
        </TestResume>

        <TestSleep>
            <status>on</status>
            <typeIndex>3</typeIndex>
            <typeString>TEST_SLEEP</typeString>
            <CLI>sleep</CLI>
            <CLIParamNum>1</CLIParamNum>
        </TestSleep>

        <TestDebug>
            <status>on</status>
            <typeIndex>4</typeIndex>
            <typeString>TEST_DEBUG</typeString>
            <CLI>debug-test</CLI>
            <CLIParamNum>0</CLIParamNum>
        </TestDebug>

        <TrafficCheck>
            <status>on</status>
            <typeIndex>12</typeIndex>
            <typeString>CHECK_TRAFFIC</typeString>
            <CLI>check-traffic</CLI>
            <CLIParamNum>0</CLIParamNum>
            <rerunInterval>10</rerunInterval>
            <maxRerunNum>3</maxRerunNum>
            <pingWait>1</pingWait>
            <pingTimeout>10</pingTimeout>
        </TrafficCheck>

        <TopoCheck>
            <status>on</status>
            <typeIndex>13</typeIndex>
            <typeString>CHECK_TOPO</typeString>
            <CLI>check-topo</CLI>
            <CLIParamNum>0</CLIParamNum>
            <rerunInterval>5</rerunInterval>
            <maxRerunNum>3</maxRerunNum>
        </TopoCheck>

        <ONOSCheck>
            <status>on</status>
            <typeIndex>14</typeIndex>
            <typeString>CHECK_ONOS</typeString>
            <CLI>check-onos</CLI>
            <CLIParamNum>0</CLIParamNum>
            <rerunInterval>10</rerunInterval>
            <maxRerunNum>3</maxRerunNum>
        </ONOSCheck>

        <RaftLogSizeCheck>
            <status>on</status>
            <typeIndex>15</typeIndex>
            <typeString>CHECK_RAFT_LOG_SIZE</typeString>
            <CLI>check-raft-size</CLI>
            <CLIParamNum>0</CLIParamNum>
        </RaftLogSizeCheck>

        <DeviceDown>
            <status>on</status>
            <typeIndex>22</typeIndex>
            <typeString>NETWORK_DEVICE_DOWN</typeString>
            <CLI>device-down</CLI>
            <CLIParamNum>1</CLIParamNum>
        </DeviceDown>

        <DeviceUp>
            <status>on</status>
            <typeIndex>23</typeIndex>
            <typeString>NETWORK_DEVICE_UP</typeString>
            <CLI>device-up</CLI>
            <CLIParamNum>1</CLIParamNum>
        </DeviceUp>

        <PortDown>
            <status>on</status>
            <typeIndex>24</typeIndex>
            <typeString>NETWORK_PORT_DOWN</typeString>
            <CLI>port-down</CLI>
            <CLIParamNum>2</CLIParamNum>
        </PortDown>

        <PortUp>
            <status>on</status>
            <typeIndex>25</typeIndex>
            <typeString>NETWORK_PORT_UP</typeString>
            <CLI>port-up</CLI>
            <CLIParamNum>2</CLIParamNum>
        </PortUp>

        <ONOSDown>
            <status>on</status>
            <typeIndex>40</typeIndex>
            <typeString>ONOS_ONOS_DOWN</typeString>
            <CLI>onos-down</CLI>
            <CLIParamNum>1</CLIParamNum>
            <rerunInterval>5</rerunInterval>
            <maxRerunNum>3</maxRerunNum>
        </ONOSDown>

        <ONOSUp>
            <status>on</status>
            <typeIndex>41</typeIndex>
            <typeString>ONOS_ONOS_UP</typeString>
            <CLI>onos-up</CLI>
            <CLIParamNum>1</CLIParamNum>
            <rerunInterval>5</rerunInterval>
            <maxRerunNum>3</maxRerunNum>
        </ONOSUp>

        <SetCfg>
            <status>on</status>
            <typeIndex>42</typeIndex>
            <typeString>ONOS_SET_CFG</typeString>
            <CLI>set-cfg</CLI>
            <CLIParamNum>3</CLIParamNum>
            <rerunInterval>5</rerunInterval>
            <maxRerunNum>3</maxRerunNum>
        </SetCfg>

        <BalanceMasters>
            <status>on</status>
            <typeIndex>44</typeIndex>
            <typeString>ONOS_BALANCE_MASTERS</typeString>
            <CLI>balance-masters</CLI>
            <CLIParamNum>0</CLIParamNum>
            <rerunInterval>5</rerunInterval>
            <maxRerunNum>3</maxRerunNum>
        </BalanceMasters>

        <addAllChecks>
            <status>on</status>
            <typeIndex>110</typeIndex>
            <typeString>CHECK_ALL</typeString>
            <CLI>check-all</CLI>
            <CLIParamNum>0</CLIParamNum>
        </addAllChecks>
    </EVENT>

    <SCHEDULER>
        <pendingEventsCapacity>1</pendingEventsCapacity>
        <runningEventsCapacity>10</runningEventsCapacity>
        <scheduleLoopSleep>0.1</scheduleLoopSleep>
    </SCHEDULER>

    <GENERATOR>
        <listenerPort>6000</listenerPort>
        <insertEventRetryInterval>1</insertEventRetryInterval>
    </GENERATOR>

    <TOPO>
        <loadTopoSleep>60</loadTopoSleep>
        <excludeNodes></excludeNodes>
    </TOPO>

    <CASE2>
        <fileName>flex.json</fileName>
        <hostFileName>flex.host</hostFileName>
    </CASE2>

    <CASE70>
        <sleepSec>60</sleepSec>
        <eventWeight>
            <port-down>2</port-down>
            <device-down>2</device-down>
            <onos-down>1</onos-down>
        </eventWeight>
        <skipSwitches>s201,s228</skipSwitches>
        <skipLinks></skipLinks>
    </CASE70>

    <CASE80>
        <filePath>/home/sdn/log-for-replay</filePath>
        <sleepTime>5</sleepTime>
        <skipChecks>off</skipChecks>
    </CASE80>
</PARAMS>
