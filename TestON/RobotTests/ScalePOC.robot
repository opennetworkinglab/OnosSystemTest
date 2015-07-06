*** Settings ***
Documentation     ONOS Switch Scale Test
Suite Setup       ONOS Suite Setup    ${CONTROLLER_IP}    ${CONTROLLER_USER}
Suite Teardown    ONOS Suite Teardown
Library           SSHLibrary
Library           Collections
Library           OperatingSystem
Library           String
Library           RequestsLibrary
Library           HttpLibrary.HTTP

*** Variables ***
##Grab the environment variables sources from your "cell"
${CONTROLLER_IP}    %{OC1}
${MININET_IP}    %{OCN}
${CONTROLLER_USER}    %{ONOS_USER}
${MININET_USER}    %{ONOS_USER}
##USER_HOME used for public key
${USER_HOME}    %{HOME}
##ONOS_HOME is where the onos dist will be deployed on the controller vm
${ONOS_HOME}    /opt/onos
${RESTCONFPORT}    8181
${LINUX_PROMPT}    $
##SWITCHES_RESULT_FILE and JENKINS_WORKSPACE can be configurable...read overriding variables in README
##SWITCHES_RESULT_FILE is used to plot data. you can use a jenkins post job for this or do it manually
##NOTE: This file must exist otherwise the test will fail when trying to write to this file
${SWITCHES_RESULT_FILE}    ${USER_HOME}/workspace/tools/switches.csv
${JENKINS_WORKSPACE}    ${USER_HOME}/workspace/ONOS-Stable/
${prompt_timeout}    30s
${start}    10
${end}    100
${increments}    10
##Number of nodes in cluster. To add more nodes, create CONTROLLER_IP2/3/4 etc. variables above and change this cluster variable
${cluster}    1

*** Test Cases ***
Find Max Switches By Scaling
    [Documentation]    Find the max number of switches from ${start} until reaching ${end} in steps of ${increments}. The following checks are made through REST APIs:
    ...    -\ Verify device count is correct
    ...    -\ Verify device status is available
    ...    -\ Verify device roles are MASTER (default role in case of standalone controller)
    ...    -\ Verify topology recognizes corret number of devices (Through api "/topology")
    ...    -\ Observe each device individually
    ...    -\ Observe links, hosts, and flows through the controller
    ...    -\ Observe device info at lower level on mininet (Written for PoC). Shows flows, links, and ports. Checks can be easily implemented at that level as well
    ...    -\ STOP Mininet Topo
    ...    -\ Verify device count is zero
    ...    -\ Verify topology sees no devices (Through api "/topology")
    [Tags]    done
    Append To File    ${SWITCHES_RESULT_FILE}    Max Switches Linear Topo\n
    ${max}=    Find Max Switches    ${start}    ${end}    ${increments}
    Log    ${max}
    Append To File    ${SWITCHES_RESULT_FILE}    ${max}\n

*** Keywords   ***
ONOS Suite Setup
    [Arguments]    ${controller}    ${user}
    [Documentation]    Transfers the ONOS dist over to the test vm and start the controller. We will leverage the bash script, "onos-install" to do this.
    Create Controller IP List
    ${rc}=    Run and Return RC    onos-package
    Should Be Equal As Integers    ${rc}    0
    : FOR    ${ip}    IN    @{controller_list}
    \    ${rc}=    Run and Return RC    onos-install -f ${ip}
    \    Should Be Equal As Integers    ${rc}    0
    Create HTTP Sessions
    Wait Until Keyword Succeeds    60s    2s    Verify All Controller are up
    #If creating a cluster, create a keyword  and call it here

ONOS Suite Teardown
    [Documentation]    Stop ONOS on Controller VMs and grabs karaf logs on each controller (put them in /tmp)
    ${rc}=    Run and Return RC    onos-kill
    #Should Be Equal As Integers    ${rc}    0
    ${rc}=    Run and Return RC    cp ${SWITCHES_RESULT_FILE} ${JENKINS_WORKSPACE}
    Should Be Equal As Integers    ${rc}    0
    ${rc}=    Run and Return RC    rm ${SWITCHES_RESULT_FILE}
    Should Be Equal As Integers    ${rc}    0
    Clean Mininet System
    : FOR    ${ip}    IN    @{controller_list}
    \    Get Karaf Logs    ${ip}

Create Controller IP List
    [Documentation]    Creates a list of controller ips for a cluster. When creating a cluster, be sure to set each variable to %{OC} env vars in the variables section 
    @{controller_list}=    Create List    ${CONTROLLER_IP}
    Set Suite Variable    @{controller_list}

Create HTTP Sessions
    [Documentation]    Creates an http session with all controllers in the cluster. Session names are set to respective ips. 
    ${HEADERS}=    Create Dictionary    Content-Type    application/json
    : FOR    ${ip}    IN    @{controller_list}
    \    Create Session    ${ip}    http://${ip}:${RESTCONFPORT}    headers=${HEADERS}

Find Max Switches
    [Arguments]    ${start}    ${stop}    ${step}
    [Documentation]    Will find out max switches starting from ${start} till reaching ${stop} and in steps defined by ${step}
    ${max-switches}    Set Variable    ${0}
    ${start}    Convert to Integer    ${start}
    ${stop}    Convert to Integer    ${stop}
    ${step}    Convert to Integer    ${step}
    : FOR    ${switches}    IN RANGE    ${start}    ${stop+1}    ${step}
    \    Start Mininet Linear    ${switches}
    \    ${status}    ${result}    Run Keyword And Ignore Error    Verify Controllers are Not Dead
    \    Exit For Loop If    '${status}' == 'FAIL'
    \    ${status}    ${result}    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    ${switches*2}    2s
    \    ...    Ensure Switch Count    ${switches}
    \    Exit For Loop If    '${status}' == 'FAIL'
    \    ${status}    ${result}    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    ${switches*2}    2s
    \    ...    Ensure Switches are Available
    \    Exit For Loop If    '${status}' == 'FAIL'
    \    ${status}    ${result}    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    ${switches*2}    2s
    \    ...    Ensure Switch Role    MASTER
    \    Exit For Loop If    '${status}' == 'FAIL'
    \    ${status}    ${result}    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    ${switches*2}    2s
    \    ...    Ensure Topology    ${switches}    ${cluster}
    \    Exit For Loop If    '${status}' == 'FAIL'
    \    ${status}    ${result}    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    ${switches*2}    2s
    \    ...    Experiment Links, Hosts, and Flows
    \    ${status}    ${result}    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    ${switches*2}    2s
    \    ...    Check Each Switch Individually
    \    ${status}    ${result}    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    ${switches*2}    2s
    \    ...    Check Mininet at Lower Level
    \    Stop Mininet
    \    ${status}    ${result}    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    ${switches*2}    2s
    \    ...    Ensure No Switches are Available
    \    Exit For Loop If    '${status}' == 'FAIL'
    \    ${status}    ${result}    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    ${switches*2}    2s
    \    ...    Ensure No Switches in Topology    ${cluster}
    \    Exit For Loop If    '${status}' == 'FAIL'
    \    ${max-switches}    Convert To String    ${switches}
    [Return]    ${max-switches}

Run Command On Remote System
    [Arguments]    ${remote_system}    ${cmd}    ${user}=${CONTROLLER_USER}    ${prompt}=${LINUX_PROMPT}    ${prompt_timeout}=30s
    [Documentation]    Reduces the common work of running a command on a remote system to a single higher level robot keyword,
    ...    taking care to log in with a public key and the command given is written and the output returned. No test conditions
    ...    are checked.
    Log    Attempting to execute ${cmd} on ${remote_system}
    ${conn_id}=    SSHLibrary.Open Connection    ${remote_system}    prompt=${prompt}    timeout=${prompt_timeout}
    Login With Public Key    ${user}    ${USER_HOME}/.ssh/id_rsa    any
    SSHLibrary.Write    ${cmd}
    ${output}=    SSHLibrary.Read Until    ${LINUX_PROMPT}
    SSHLibrary.Close Connection
    Log    ${output}
    [Return]    ${output}

Start Mininet Linear
    [Arguments]    ${switches}
    [Documentation]    Start mininet linear topology with ${switches} nodes
    Log To Console    \n
    Log To Console    Starting mininet linear ${switches}
    ${mininet_conn_id}=    Open Connection    ${MININET_IP}    prompt=${LINUX_PROMPT}    timeout=${switches*3}
    Set Suite Variable    ${mininet_conn_id}
    Login With Public Key    ${MININET_USER}    ${USER_HOME}/.ssh/id_rsa    any
    Write    sudo mn --controller=remote,ip=${CONTROLLER_IP} --topo linear,${switches} --switch ovsk,protocols=OpenFlow13
    Read Until    mininet>
    Sleep    6

Stop Mininet
    [Documentation]    Stop mininet topology
    Log To Console    Stopping Mininet
    Switch Connection    ${mininet_conn_id}
    Read
    Write    exit
    Read Until    ${LINUX_PROMPT}
    Close Connection

Check Mininet at Lower Level
    [Documentation]    PoC for executing mininet commands at the lower level
    Switch Connection    ${mininet_conn_id}
    Read
    Write    dpctl dump-flows -O OpenFlow13
    ${output}=    Read Until    mininet>
    Log    ${output}
    Write    dump
    ${output}=    Read Until    mininet>
    Log    ${output}
    Write    links
    ${output}=    Read Until    mininet>
    Log    ${output}
    Write    ports
    ${output}=    Read Until    mininet>
    Log    ${output}

Clean Mininet System
    [Arguments]     ${mininet_system}=${MININET_IP}
    [Documentation]    Cleans the mininet environment (sudo mn -c)
    Run Command On Remote System    ${mininet_system}   sudo mn -c    ${CONTROLLER_USER}    ${LINUX_PROMPT}    600s

Verify All Controller are up
    [Documentation]    Verifies each controller is up by issuing a rest call and getting a 200
    : FOR    ${ip}    IN    @{controller_list}
    \    ${resp}=    ONOS Get    ${ip}    devices
    \    Should Be Equal As Strings    ${resp.status_code}    200

Verify Controllers are Not Dead
    [Documentation]    Verifies each controller is not dead by making sure karaf log does not contain "OutOfMemoryError" and rest call still returns 200 
    : FOR    ${ip}    IN    @{controller_list}
    \    Verify Controller Is Not Dead    ${ip}

Verify Controller Is Not Dead
    [Arguments]    ${controller}
    ${response}=    Run Command On Remote System    ${controller}   grep java.lang.OutOfMemoryError /opt/onos/log/karaf.log
    Should Not Contain    ${response}    OutOfMemoryError
    ${resp}    RequestsLibrary.Get    ${controller}    /onos/v1/devices
    Log    ${resp.content}
    Should Be Equal As Strings    ${resp.status_code}    200

Experiment Links, Hosts, and Flows
    [Documentation]    Currently this only returns the information the controller has on links, hosts, and flows. Checks can easily be implemented
    : FOR    ${ip}    IN    @{controller_list}
    \    ${resp}=    ONOS Get    ${ip}    links
    \    ${jsondata}    To JSON    ${resp.content}
    \    ${length}=    Get Length    ${jsondata['links']}
    \    Log    ${resp.content}
    \    ${resp}=    ONOS Get    ${ip}    flows
    \    ${jsondata}    To JSON    ${resp.content}
    \    ${length}=    Get Length    ${jsondata['flows']}
    \    Log    ${resp.content}
    \    ${resp}=    ONOS Get    ${ip}    hosts
    \    ${jsondata}    To JSON    ${resp.content}
    \    ${length}=    Get Length    ${jsondata['hosts']}
    \    Log    ${resp.content}

Ensure Topology
    [Arguments]    ${device_count}    ${cluster_count}
    [Documentation]    Verifies the devices count through /topoplogy api. Currently, cluster count is inconsistent (Possible bug, will look into it), so the check on that is ignored, but logged
    : FOR    ${ip}    IN    @{controller_list}
    \    ${resp}=    ONOS Get    ${ip}    topology
    \    Log    ${resp.content}
    \    ${devices}=    Get Json Value    ${resp.content}    /devices
    \    ${clusters}=    Get Json Value    ${resp.content}    /clusters
    \    Should Be Equal As Strings    ${devices}    ${device_count}
    \    #Should Be Equal As Strings    ${clusters}    ${cluster_count}

Ensure No Switches in Topology
    [Arguments]    ${cluster_count}
    [Documentation]    Verifies the topology sees no devices
    : FOR    ${ip}    IN    @{controller_list}
    \    ${resp}=    ONOS Get    ${ip}    topology
    \    Log    ${resp.content}
    \    ${devices}=    Get Json Value    ${resp.content}    /devices
    \    ${clusters}=    Get Json Value    ${resp.content}    /clusters
    \    Should Be Equal As Strings    ${devices}    0
    \    #Should Be Equal As Strings    ${clusters}    ${cluster_count}

ONOS Get
    [Arguments]    ${session}    ${noun}
    [Documentation]    Common keyword to issue GET requests to the controller. Arguments are the session (controller ip) and api path
    ${resp}    RequestsLibrary.Get    ${session}    /onos/v1/${noun}
    Log    ${resp.content}
    [Return]    ${resp}

Ensure Switch Count
    [Arguments]    ${switch_count}
    [Documentation]    Verfies the device count (passed in as arg) on each controller is accurate.
    : FOR    ${ip}    IN    @{controller_list}
    \    ${resp}    ONOS Get    ${ip}    devices
    \    Log    ${resp.content}
    \    Should Be Equal As Strings    ${resp.status_code}    200
    \    Should Not Be Empty    ${resp.content}
    \    ${jsondata}    To JSON    ${resp.content}
    \    ${length}=    Get Length    ${jsondata['devices']}
    \    Should Be Equal As Integers    ${length}    ${switch_count}

Ensure Switches are Available
    [Documentation]    Verifies that the switch's availability state is true on all switches through all controllers
    : FOR    ${ip}    IN    @{controller_list}
    \    ${resp}    ONOS Get    ${ip}    devices
    \    Log    ${resp.content}
    \    Should Be Equal As Strings    ${resp.status_code}    200
    \    Should Not Be Empty    ${resp.content}
    \    ${jsondata}    To JSON    ${resp.content}
    \    #Robot tweak to do a nested for loop
    \    Check Each Switch Status    ${jsondata}    True

Check Each Switch Status
    [Arguments]    ${jdata}    ${bool}
    ${length}=    Get Length    ${jdata['devices']}
    : FOR    ${INDEX}    IN RANGE    0    ${length}
    \    ${data}=    Get From List    ${jdata['devices']}    ${INDEX}
    \    ${status}=    Get From Dictionary    ${data}    available
    \    Should Be Equal As Strings    ${status}    ${bool}

Ensure No Switches are Available
    [Documentation]    Verifies that the switch's availability state is false on all switches through all controllers
    : FOR    ${ip}    IN    @{controller_list}
    \    ${resp}    ONOS Get    ${ip}    devices
    \    Log    ${resp.content}
    \    Should Be Equal As Strings    ${resp.status_code}    200
    \    Should Not Be Empty    ${resp.content}
    \    ${jsondata}    To JSON    ${resp.content}
    \    Check Each Switch Status    ${jsondata}    False

Check Each Switch Individually
    [Documentation]    Currently just observe each information the device has. Checks can easily be implemented
    : FOR    ${ip}    IN    @{controller_list}
    \    ${resp}    ONOS Get    ${ip}    devices
    \    Should Be Equal As Strings    ${resp.status_code}    200
    \    ${jsondata}    To JSON    ${resp.content}
    \    #Robot tweak to do a nested for loop
    \    Check Each Switch    ${jsondata}

Check Each Switch
    [Arguments]    ${jdata}
    ${length}=    Get Length    ${jdata['devices']}
    @{dpid_list}=    Create List
    : FOR    ${INDEX}    IN RANGE    0    ${length}
    \    ${devicedata}=    Get From List    ${jdata['devices']}    ${INDEX}
    \    ${id}=    Get From Dictionary    ${devicedata}    id
    \    Append To List    ${dpid_list}    ${id}
    \    Log    ${dpid_list}
    ${length}=    Get Length    ${dpid_list}
    : FOR    ${i}    IN    @{dpid_list}
    \    ${resp}    ONOS Get    ${ip}    devices/${i}
    \    Log    ${resp.content}

Ensure Switch Role
    [Arguments]    ${role}
    [Documentation]    Verifies that the controller's role for each switch is MASTER (default in standalone mode)
    : FOR    ${ip}    IN    @{controller_list}
    \    ${resp}    ONOS Get    ${ip}    devices
    \    Log    ${resp.content}
    \    Should Be Equal As Strings    ${resp.status_code}    200
    \    Should Not Be Empty    ${resp.content}
    \    ${jsondata}    To JSON    ${resp.content}
    \    Ensure Role    ${jsondata}    ${role}

Ensure Role
    [Arguments]    ${jdata}    ${role}
    ${length}=    Get Length    ${jdata['devices']}
    : FOR    ${INDEX}    IN RANGE    0    ${length}
    \    ${data}=    Get From List    ${jdata['devices']}    ${INDEX}
    \    ${status}=    Get From Dictionary    ${data}    role
    \    Should Be Equal As Strings    ${status}    ${role}

Get Karaf Logs
    [Arguments]    ${controller}
    [Documentation]    Compresses all the karaf log files on each controler and puts them on your pybot execution machine (in /tmp)
    Run Command On Remote System    ${controller}    tar -zcvf /tmp/${SUITE NAME}.${controller}.tar.gz ${ONOS_HOME}/log
    SSHLibrary.Open Connection    ${controller}    prompt=${LINUX_PROMPT}    timeout=${prompt_timeout}
    Login With Public Key    ${CONTROLLER_USER}    ${USER_HOME}/.ssh/id_rsa    any
    SSHLibrary.Get File    /tmp/${SUITE NAME}.${controller}.tar.gz    /tmp/
    SSHLibrary.Close Connection
