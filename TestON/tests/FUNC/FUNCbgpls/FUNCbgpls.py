"""
Copyright 2016 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.

**** Scripted by Antony Silvester  - antony.silvester@huawei.com ******


This Test check the bgp_ls functionality

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Discovery the topology using BGPLS
CASE3: Addition of new Node to existing topology
CASE4: Verification of Links thats is discovered"
CASE5: Deletion of Links
Case6: Uninstalling the app


"""
class FUNCbgpls:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        CASE1 is to compile ONOS and push it to the test machines

        Startup sequence:
        cell <name>
        onos-verify-cell
        NOTE: temporary - onos-remove-raft-logs
        onos-uninstall
        git pull
        onos-package
        onos-install -f
        onos-wait-for-start
        start cli sessions
        start BGPLS apps

        """
        import os

        main.log.info( "ONOS Single node start " +
                         "Scapy Tool - initialization" )
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        try:
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.ipList = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
            main.scapy_ip = os.getenv( main.params[ 'SCAPY' ][ 'HOSTNAMES' ] )

            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            stepResult = main.testSetUp.envSetup()
        except Exception as e:
            main.testSetUp.envSetupException( e )

        cliResults = main.testSetUp.ONOSSetUp( main.Cluster, cellName=main.cellName,
                                               mininetIp=main.scapy_ip )
        main.step( "App Ids check" )
        appCheck = main.Cluster.active( 0 ).CLI.appToIDCheck()

        if appCheck != main.TRUE:
            main.log.warn( main.Cluster.active( 0 ).CLI.apps() )
            main.log.warn( main.Cluster.active( 0 ).CLI.appIDs() )
            utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                     onpass="App Ids seem to be correct",
                                     onfail="Something is wrong with app Ids" )
        if cliResults == main.FALSE:
            main.log.error( "Failed to start ONOS,stopping test" )
            main.cleanAndExit()

    def CASE2( self, main ):
        """
        Discovery the topology using BGPLS
        """
        import os
        import sys
        import re
        import time

        main.case( "Testcase 2 : Discovery the Network Topology using BGPLS" )
        main.Cluster.active( 0 ).CLI.log( "\"testcase2 start\"" )

        try:
            from tests.FUNC.FUNCbgpls.dependencies.Nbdata import BgpLs
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanAndExit()

        bgplsConfig = BgpLs()
        Ne_id = bgplsConfig.Constants()
        app = bgplsConfig.apps()
        httpport = main.params[ 'HTTP' ][ 'port' ]
        path = main.params[ 'HTTP' ][ 'path' ]
        bgplsConfig.ipValue( main.ipList, main.scapy_ip )

        bgplsConfig.Comments()
        main.log.info( "Sending BGPLS information" )
        bgplsConfig.Comments()

        main.Scapy1.handle.sendline( "sudo python  OnosSystemTest/TestON/tests/FUNC/FUNCbgpls/\
        dependencies/Scapyfiles/Topo_discovery.py" )
        bgplsConfig.Comments()
        main.log.info( "Enable BGPlS plugin in ONOS" )
        bgplsConfig.Comments()

        main.testSetUp.startOnosClis( main.Cluster )

        installResults = main.Cluster.active( 0 ).CLI.activateApp( app[ 0 ] )
        main.step( "Install onos-app-bgp" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-bgp successful",
                                 onfail="Install onos-app-bgp failed" )

        bgpls_post = bgplsConfig.DictoJson()

        bgplsConfig.Comments()
        main.log.info( "BGPLS RestConf input" )
        bgplsConfig.Comments()

        print ( bgpls_post )
        Poststatus, result = main.Cluster.active( 0 ).REST.send( '/network/configuration/', method="POST", data=bgpls_post )
        main.step( "Configure BGP through RESTCONF" )

        utilities.assert_equals( expect='200',
                                 actual=Poststatus,
                                 onpass="Post Port Success",
                                 onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )

        bgplsConfig.Comments()
        main.step( "Check Network devices are Updated in ONOS " )
        bgplsConfig.Comments()
        time.sleep( 15 )
        response = main.Cluster.active( 0 ).CLI.devices()
        responseCheck = main.FALSE
        if response:
            responseCheck = main.TRUE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=responseCheck,
                                 onpass="Network Devices update in ONOS successful",
                                 onfail="Network Devices update in ONOS failed" )

        main.step( "Check the nodes are discovered" )
        if response.find( Ne_id[ 1 ][ 0 ] ) and response.find( Ne_id[ 1 ][ 1 ] ) and response.find( Ne_id[ 1 ][ 2 ] ) != -1:
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Node " + str( Ne_id[ 1 ][ 0 ] ) + ( Ne_id[ 1 ][ 1 ] ) + ( Ne_id[ 1 ][ 2 ] ) + "  sucess",
                                 onfail="Node " + str( Ne_id[ 1 ][ 0 ] ) + ( Ne_id[ 1 ][ 1 ] ) + ( Ne_id[ 1 ][ 2 ] ) + " failed" )
        main.Cluster.active( 0 ).CLI.log( "\"testcase2 end\"" )

        main.step( "Check for Errors or Exception in testcase2" )
        startStr = "testcase2 start"
        endStr = "testcase2 end"
        errorLog = main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress,
                                             [ "ERROR", "EXCEPT" ], "s",
                                             startStr, endStr )
        utilities.assert_equals( expect=0, actual=errorLog,
                                 onpass="No Exception or Error occured in testcase2",
                                 onfail="Exception or Error occured in testcase2" )
        bgplsConfig.Comments()
        main.log.info( "Kill Scapy process" )
        bgplsConfig.Comments()

        main.Scapy1.handle.send( "\x03" )
        time.sleep( 90 )  # This Sleep time gives time for the socket to close.

    def CASE3( self, main ):
        """
        Addition of new Node to existing topology
        """
        import os
        import sys
        import re
        import time

        main.case( "Testcase 3: Addition of New Node to existing topology" )
        main.Cluster.active( 0 ).CLI.log( "\"testcase3 start\"" )
        try:
            from tests.FUNC.FUNCbgpls.dependencies.Nbdata import BgpLs
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanAndExit()

        bgplsConfig = BgpLs()
        Ne_id = bgplsConfig.Constants()
        app = bgplsConfig.apps()

        httpport = main.params[ 'HTTP' ][ 'port' ]
        path = main.params[ 'HTTP' ][ 'path' ]

        bgplsConfig.ipValue( main.ipList, main.scapy_ip )

        bgplsConfig.Comments()
        main.log.info( "Sending BGPLS Packet " )
        bgplsConfig.Comments()

        main.Scapy1.handle.sendline( "sudo python  OnosSystemTest/TestON/tests/FUNC/FUNCbgpls/\
        dependencies/Scapyfiles/Update_Node.py" )
        bgplsConfig.Comments()
        main.log.info( "Enable BGPlS plugin in ONOS" )
        bgplsConfig.Comments()

        main.step( "UnInstall onos-app-bgp" )
        installResults = main.Cluster.active( 0 ).CLI.deactivateApp( app[ 0 ] )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Uninstall  onos-app-bgp successful",
                                 onfail="Uninstall  onos-app-bgp failed" )

        installResults = main.Cluster.active( 0 ).CLI.activateApp( app[ 0 ] )
        main.step( "Install onos-app-bgp" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-bgp successful",
                                 onfail="Install onos-app-bgp failed" )

        bgpls_post = bgplsConfig.DictoJson()

        bgplsConfig.Comments()
        main.log.info( "BGPLS RestConf input" )
        bgplsConfig.Comments()

        bgplsConfig.Comments()
        main.step( "Check Network devices are Updated in ONOS" )
        bgplsConfig.Comments()
        time.sleep( 120 )
        response = main.Cluster.active( 0 ).CLI.devices()

        responseCheck = main.FALSE
        if response:
            responseCheck = main.TRUE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=responseCheck,
                                 onpass="Network Devices update in ONOS successful",
                                 onfail="Network Devices update in ONOS failed" )
        main.step( "Check Newly added Node is getting updated" )

        if response.find( Ne_id[ 1 ][ 3 ] ) != -1:
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Node " + str( Ne_id[ 1 ][ 3 ] ) + " update  sucess",
                                 onfail="Node " + str( Ne_id[ 1 ][ 3 ] ) + " update failed" )
        main.Cluster.active( 0 ).CLI.log( "\"testcase3 end\"" )

        main.step( "Check for Errors or Exception in testcase3" )
        startStr = "testcase3 start"
        endStr = "testcase3 end"
        errorLog = main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress,
                                             [ "ERROR", "EXCEPT" ], "s",
                                             startStr, endStr )
        utilities.assert_equals( expect=0, actual=errorLog,
                                 onpass="No Exception or Error occured in testcase3",
                                 onfail="Exception or Error occured in testcase3" )
        bgplsConfig.Comments()
        main.log.info( "Kill Scapy process" )
        bgplsConfig.Comments()
        main.Scapy1.handle.send( "\x03" )
        time.sleep( 90 )  # This Sleep time gives time for the socket to close.

    def CASE4( self, main ):
        """
        Verification of Links in existing topology
        """
        import json
        import time
        import os
        main.case( "Testcase 4: Verification of Links thats is discovered" )
        main.Cluster.active( 0 ).CLI.log( "\"testcase4 start\"" )
        try:
            from tests.FUNC.FUNCbgpls.dependencies.Nbdata import BgpLs
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanAndExit()

        bgplsConfig = BgpLs()
        app = bgplsConfig.apps()
        bgplsConfig.ipValue( main.ipList, main.scapy_ip )

        bgplsConfig.Comments()
        main.log.info( "Sending BGPLS Link information Packet " )
        bgplsConfig.Comments()

        main.Scapy1.handle.sendline( "sudo python  OnosSystemTest/TestON/tests/FUNC/FUNCbgpls/dependencies/Scapyfiles/Link_Update_Node.py" )
        bgplsConfig.Comments()
        main.log.info( "Enable BGPlS plugin in ONOS" )
        bgplsConfig.Comments()

        main.step( "UnInstall onos-app-bgp" )
        installResults = main.Cluster.active( 0 ).CLI.deactivateApp( app[ 0 ] )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Uninstall  onos-app-bgp successful",
                                 onfail="Uninstall  onos-app-bgp failed" )

        installResults = main.Cluster.active( 0 ).CLI.activateApp( app[ 0 ] )
        main.step( "Install onos-app-bgp" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-bgp successful",
                                 onfail="Install onos-app-bgp failed" )
        bgplsConfig.Comments()
        main.step( "Checking the Link Discovery Status" )
        bgplsConfig.Comments()
        time.sleep( 120 )   # Time taken to discovery the links
        response = main.Cluster.active( 0 ).CLI.links()
        linksResp = json.loads( response )
        check_link = bgplsConfig.checkLinks( linksResp )
        reply_Check_Link = main.FALSE
        if check_link:
            reply_Check_Link = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=reply_Check_Link,
                                 onpass="Link Discovery Success.",
                                 onfail="Link Discovery Failed." )
        main.Cluster.active( 0 ).CLI.log( "\"testcase4 end\"" )

        main.step( "Check for Errors or Exception in testcase4 " )
        startStr = "testcase4 start"
        endStr = "testcase4 end"
        errorLog = main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress,
                                             [ "ERROR", "EXCEPT" ], "s",
                                             startStr, endStr )
        utilities.assert_equals( expect=0, actual=errorLog,
                                 onpass="No Exception or Error occured in testcase4",
                                 onfail="Exception or Error occured in testcase4" )
        bgplsConfig.Comments()
        main.log.info( "Kill Scapy process" )
        bgplsConfig.Comments()
        main.Scapy1.handle.send( "\x03" )
        time.sleep( 90 )

    def CASE5( self, main ):
        """
        Deletion of  links
        """
        import json
        import time
        import os
        main.case( "Testcase 5: Deletion of Link in existing topology" )

        main.Cluster.active( 0 ).CLI.log( "\"testcase5 start\"" )
        try:
            from tests.FUNC.FUNCbgpls.dependencies.Nbdata import BgpLs
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanAndExit()

        bgplsConfig = BgpLs()
        app = bgplsConfig.apps()
        bgplsConfig.ipValue( main.ipList, main.scapy_ip )

        bgplsConfig.Comments()
        main.log.info( "Sending BGPLS Delete Link Packet " )
        bgplsConfig.Comments()

        main.Scapy1.handle.sendline( "sudo python  OnosSystemTest/TestON/tests/FUNC/FUNCbgpls/dependencies/Scapyfiles/Deletion_Node.py" )
        bgplsConfig.Comments()
        main.log.info( "Enable BGPlS plugin in ONOS " )
        bgplsConfig.Comments()

        main.step( "UnInstall onos-app-bgp" )
        installResults = main.Cluster.active( 0 ).CLI.deactivateApp( app[ 0 ] )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Uninstall  onos-app-bgp successful",
                                 onfail="Uninstall  onos-app-bgp failed" )

        installResults = main.Cluster.active( 0 ).CLI.activateApp( app[ 0 ] )
        main.step( "Install onos-app-bgp" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-bgp successful",
                                 onfail="Install onos-app-bgp failed" )
        bgplsConfig.Comments()
        main.step( "Checking whether the links is deleted" )
        bgplsConfig.Comments()
        time.sleep( 120 )  # Time taken to discovery the links
        response = main.Cluster.active( 0 ).CLI.links()
        linksResp = json.loads( response )
        check_link = bgplsConfig.checkLinks( linksResp )
        reply_Check_Link = main.FALSE
        if not check_link:
            reply_Check_Link = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=reply_Check_Link,
                                 onpass="Link is Deleted Successfully.",
                                 onfail="Link is Deletion Failed." )
        main.Cluster.active( 0 ).CLI.log( "\"testcase5 end\"" )

        main.step( "Check for Errors or Exception in testcase5" )
        startStr = "testcase5 start"
        endStr = "testcase5 end"
        errorLog = main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress,
                                             [ "ERROR", "EXCEPT" ], "s",
                                             startStr, endStr )
        utilities.assert_equals( expect=0, actual=errorLog,
                                 onpass="No Exception or Error occured in testcase5",
                                 onfail="Exception or Error occured in testcase5" )
        bgplsConfig.Comments()
        main.log.info( "Kill Scapy process" )
        bgplsConfig.Comments()
        main.Scapy1.handle.send( "\x03" )
        time.sleep( 90 )

    def CASE6( self, main ):
        """
        Uninstalling the app
        """
        import os
        import sys
        import re
        import time

        main.case( "TestCase 6: UnInstalling of app" )
        main.Cluster.active( 0 ).CLI.log( "\"testcase6 start\"" )
        try:
            from tests.FUNC.FUNCbgpls.dependencies.Nbdata import BgpLs
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanAndExit()

        bgplsConfig = BgpLs()
        app = bgplsConfig.apps()

        bgplsConfig = BgpLs()
        bgplsConfig.ipValue( main.ipList, main.scapy_ip )

        main.testSetUp.createApplyCell( main.Cluster, True, main.cellName, main.apps, main.scapy_ip, True, main.ipList )
        bgplsConfig.Comments()
        main.testSetUp.startOnosClis( main.Cluster )
        bgplsConfig.Comments()

        main.log.info( "Uninstall onos-app-bgp" )
        bgplsConfig.Comments()
        main.step( "UnInstall onos-app-bgp" )
        installResults = main.Cluster.active( 0 ).CLI.deactivateApp( app[ 0 ] )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Uninstall  onos-app-bgp successful",
                                 onfail="Uninstall  onos-app-bgp failed" )

        main.Cluster.active( 0 ).CLI.log( "\"testcase6 end\"" )
        main.step( "Check for Errors or Exception in testcase6" )
        startStr = "testcase6 start"
        endStr = "testcase6 end"
        errorLog = main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress,
                                             [ "ERROR", "EXCEPT" ], "s",
                                             startStr, endStr )
        utilities.assert_equals( expect=0, actual=errorLog,
                                 onpass="No Exception or Error occured in testcase6",
                                 onfail="Exception or Error occured in testcase6" )

        main.step( "Check for Errors or Exception End of the Script" )
        errorLog = main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress,
                                             [ "ERROR", "EXCEPT" ] )
        utilities.assert_equals( expect=0, actual=errorLog,
                                 onpass="No Exception or Error occured",
                                 onfail="Exception or Error occured" )
