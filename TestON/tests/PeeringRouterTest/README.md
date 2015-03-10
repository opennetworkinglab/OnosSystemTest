

1) Install TestON framework from https://github.com/srikanthvavila/ONLabTest (Follow README instructions. Until forked repo is mrged back, use URL https://github.com/srikanthvavila/ONLabTest for cloning this repo. You can ignore Linc-OE and STS installation steps as we may not need them for now)

2) Peering router testcases are under ~/TestON/tests/PeeringRouterTest folder:
a) CASE4 - Basic Route advertisement and connectivity in untagged network
b) CASE5 - Basic Route advertisement and connectivity in tagged network
c) CASE7 - Scale test with 25k routes
d) CASE21 - Route convergence due to bgp peering session flapping in untagged network
e) CASE22 - Basic Route advertisement and connectivity in untagged network with Route server
f) CASE31 - Route convergence due to bgp peering session flapping in tagged network
g) CASE32 - Basic Route advertisement and connectivity in tagged network with Route server

3) Before running the testcases, ensure quagga is installed on the machine:
a) "sudo apt-get install quagga"
b) "Create a folder for /usr/local/var/run/quagga" 
c) "chmod 777" to quagga folder

4) Test environment assumes the TestON, ONOS and Mininet all are running in the same VM. These testcases are not verified with the components running in separate VMs.

5) Before running testcases, edit the following files and make necessary changes:
a) ~/TestON/tests/PeeringRouterTest/PeeringRouterTest.params --> Edit "cellname", "test home folder" and "controller IP" fields
b) ~/TestON/tests/PeeringRouterTest/PeeringRouterTest.topo --> Edit "host", "user", "password", "home" fields under "ONOSbench", "ONOSCli" and "ONOS1". Similalry edit "user" field under "QuaggaCliHost<>" (You can use the same user name as your mininet VM)
d) ~/TestON/drivers/common/cli/onosclidriver.py --> Change the line "self.handle.expect( "ONOS_CELL=" + str( cellname ) )" to "self.handle.expect( "ONOS_CELL" )"

6) Ensure the ONOS cell file has the following lines populated:
OCI=127.0.0.1
OC1=127.0.0.1
OC2=127.0.0.1
OCN=127.0.0.1
ONOS_FEATURES=webconsole,onos-api,onos-core-trivial,onos-cli,onos-openflow,onos-gui,onos-rest,onos-app-config,onos-app-proxyarp
ONOS_USER=<user>
ONOS_GROUP=<user>
ONOS_NIC=127.0.0.*

7) Ensure KARAF_ROOT is set to "/opt/onos/apache-karaf-3.0.2"

8) Ensure JAVA_HOME is unset before sourcing ~/onos/tools/dev/bash_profile

9) Ensure "onos-package" operation is done before executing the test cases

10) Update the testcases to be run in ~/TestON/tests/PeeringRouterTest/PeeringRouterTest.params and execute "./cly.py run PeeringRouterTest" from ~/TestON/bin folder.
