"""
Description: This test is to check onos set configuration and flows with ovsdb connection.

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Test ovsdb connection and tearDown
CASE3: Test default br-int configuration and vxlan port
CASE4: Test default openflow configuration
CASE5: Test default flows
CASE6: Configure Network Subnet Port And Check On ONOS
CASE7: Test host go online and ping each other
zhanghaoyu7@huawei.com
"""
import os

class FUNCovsdbtest:

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
        start mininet
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        start cli sessions
        start ovsdb
        start vtn apps
        """
        import os
        main.log.info( "ONOS Single node start " +
                         "ovsdb test - initialization" )
        main.case( "Setting up test environment" )
        main.caseExplanation = "Setup the test environment including " +\
                                "installing ONOS, start ONOS."

        # load some variables from the params file
        PULLCODE = False
        if main.params[ 'GIT' ][ 'pull' ] == 'True':
            PULLCODE = True
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ipList = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        OVSDB1Ip = os.getenv( main.params[ 'OVSDB' ][ 'ip1' ] )
        OVSDB2Ip = os.getenv( main.params[ 'OVSDB' ][ 'ip2' ] )

        main.step( "Create cell file" )
        cellAppString = main.params[ 'ENV' ][ 'cellApps' ]
        main.ONOSbench.createCellFile( main.ONOSbench.ip_address, cellName,
                                       main.OVSDB1.ip_address,
                                       cellAppString, ipList )

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        main.log.info( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()

        main.CLIs = []
        main.nodes = []
        main.numCtrls= 1

        for i in range( 1, main.numCtrls + 1 ):
            try:
                main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )
                main.nodes.append( getattr( main, 'ONOS' + str( i ) ) )
                ipList.append( main.nodes[ -1 ].ip_address )
            except AttributeError:
                break

        main.log.info( "Uninstalling ONOS" )
        for node in main.nodes:
            main.ONOSbench.onosUninstall( node.ip_address )

        # Make sure ONOS process is not running
        main.log.info( "Killing any ONOS processes" )
        killResults = main.TRUE
        for node in main.nodes:
            killed = main.ONOSbench.onosKill( node.ip_address )
            killResults = killResults and killed

        cleanInstallResult = main.TRUE
        gitPullResult = main.TRUE
        main.step( "Git checkout and pull" + gitBranch )
        if PULLCODE:
            main.ONOSbench.gitCheckout( gitBranch )
            gitPullResult = main.ONOSbench.gitPull()
            # values of 1 or 3 are good
            utilities.assert_lesser( expect=0, actual=gitPullResult,
                                      onpass="Git pull successful",
                                      onfail="Git pull failed" )

        main.ONOSbench.getVersion( report=True )

        main.step( "Using mvn clean install" )
        cleanInstallResult = main.TRUE
        if PULLCODE and gitPullResult == main.TRUE:
            cleanInstallResult = main.ONOSbench.cleanInstall()
        else:
            main.log.warn( "Did not pull new code so skipping mvn" +
                           "clean install" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=cleanInstallResult,
                                 onpass="MCI successful",
                                 onfail="MCI failed" )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        utilities.assert_equals( expect=main.TRUE,
                                     actual=packageResult,
                                     onpass="Successfully created ONOS package",
                                     onfail="Failed to create ONOS package" )

        main.step( "Installing ONOS package" )
        onosInstallResult = main.ONOSbench.onosInstall(
                options="-f", node=main.nodes[0].ip_address )
        utilities.assert_equals( expect=main.TRUE, actual=onosInstallResult,
                                 onpass="ONOS install successful",
                                 onfail="ONOS install failed" )

        main.step( "Checking if ONOS is up yet" )
        print main.nodes[0].ip_address
        for i in range( 2 ):
            onos1Isup = main.ONOSbench.isup( main.nodes[0].ip_address )
            if onos1Isup:
                break
        utilities.assert_equals( expect=main.TRUE, actual=onos1Isup,
                                 onpass="ONOS startup successful",
                                 onfail="ONOS startup failed" )
        main.log.step( "Starting ONOS CLI sessions" )
        print main.nodes[0].ip_address
        cliResults = main.ONOScli1.startOnosCli( main.nodes[0].ip_address )
        utilities.assert_equals( expect=main.TRUE, actual=cliResults,
                                 onpass="ONOS cli startup successful",
                                 onfail="ONOS cli startup failed" )

        main.step( "App Ids check" )
        appCheck = main.ONOScli1.appToIDCheck()

        if appCheck !=main.TRUE:
            main.log.warn( main.CLIs[0].apps() )
            main.log.warn( main.CLIs[0].appIDs() )
            utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )
        if cliResults == main.FALSE:
            main.log.error( "Failed to start ONOS,stopping test" )
            main.cleanup()
            main.exit()

        main.step( "Install onos-ovsdatabase" )
        installResults = main.ONOScli1.activateApp( "org.onosproject.ovsdb" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-ovsdatabase successful",
                                 onfail="Install onos-ovsdatabase failed" )

        main.step( "Install onos-app-vtnrsc" )
        installResults = main.ONOScli1.activateApp( "org.onosproject.vtnrsc" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-vtnrsc successful",
                                 onfail="Install onos-app-vtnrsc failed" )

        main.step( "Install onos-app-vtn" )
        installResults = main.ONOScli1.activateApp( "org.onosproject.vtn" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-vtn successful",
                                 onfail="Install onos-app-vtn failed" )

        main.step( "Install onos-app-vtnweb" )
        installResults = main.ONOScli1.activateApp( "org.onosproject.vtnweb" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-vtnweb successful",
                                 onfail="Install onos-app-vtnweb failed" )

    def CASE2( self, main ):

        """
        Test ovsdb connection and teardown
        """
        import os,sys
        import re
        import time

        main.case( "Test ovsdb connection and teardown" )
        main.caseExplanation = "Test ovsdb connection create and delete" +\
                                " over ovsdb node and onos node "

        ctrlip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        ovsdbport = main.params[ 'CTRL' ][ 'ovsdbport' ]
        delaytime = main.params[ 'TIMER' ][ 'delaytime' ]

        main.step( "Set ovsdb node manager" )
        assignResult = main.OVSDB1.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Set ovsdb node manager sucess",
                                 onfail="Set ovsdb node manager failed" )

        main.step( "Check ovsdb node manager is " + str( ctrlip ) )
        response = main.OVSDB1.getManager()
        if re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check ovsdb node manager is " + str( response ) ,
                                 onfail="Check ovsdb node manager failed" )

        main.step( "Delete ovsdb node manager" )
        deleteResult = main.OVSDB1.delManager( delaytime=delaytime )
        stepResult = deleteResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node delete manager sucess",
                                 onfail="ovsdb node delete manager failed" )

        main.step( "Check ovsdb node delete manager " + str( ctrlip ) )
        response = main.OVSDB1.getManager()
        if not re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Check ovsdb node delete manager sucess",
                                 onfail="Check ovsdb node delete manager failed" )

    def CASE3( self, main ):

        """
        Test default br-int configuration and vxlan port
        """
        import re
        import time
        import os,sys

        main.case( "Test default br-int configuration and vxlan port" )
        main.caseExplanation = "onos create default br-int bridge and" +\
                                " vxlan port on the ovsdb node"

        ctrlip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        ovsdbport = main.params[ 'CTRL' ][ 'ovsdbport' ]
        delaytime = main.params[ 'TIMER' ][ 'delaytime' ]

        main.step( "ovsdb node 1 set ovs manager to " + str( ctrlip ) )
        assignResult = main.OVSDB1.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 1 set ovs manager to  to " +\
                                  str( ctrlip ) + " sucess",
                                 onfail="ovsdb node 1 set ovs manager to  to " +\
                                  str( ctrlip ) + " failed" )

        main.step( "ovsdb node 2 set ovs manager to " + str( ctrlip ) )
        assignResult = main.OVSDB2.setManager( ip=ctrlip, port=ovsdbport, delaytime=delaytime )
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 2 set ovs manager to  to " +\
                                  str( ctrlip ) + " sucess",
                                 onfail="ovsdb node 2 set ovs manager to  to " +\
                                  str( ctrlip ) + " failed" )

        main.step( "Check ovsdb node 1 manager is " + str( ctrlip ) )
        response = main.OVSDB1.getManager()
        if re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 1 manager is " + str( response ) ,
                                 onfail="ovsdb node 1 manager check failed" )

        main.step( "Check ovsdb node 2 manager is " + str( ctrlip ) )
        response = main.OVSDB2.getManager()
        if re.search( ctrlip, response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ovsdb node 2 manager is " + str( response ) ,
                                 onfail="ovsdb node 2 manager check failed" )

        main.step( "Check default br-int bridge on ovsdb node " + str( OVSDB1Ip ) )
        response = main.OVSDB1.listBr()
        if re.search( "br-int", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="onos add default bridge on the node 1 sucess",
                                 onfail="onos add default bridge on the node 1 failed" )

        main.step( "Check default br-int bridge on ovsdb node " + str( OVSDB2Ip ) )
        response = main.OVSDB2.listBr()
        if re.search( "br-int", response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="onos add default bridge on the node 2 sucess",
                                 onfail="onos add default bridge on the node 2 failed" )

        main.step( "Check default vxlan port on ovsdb node " + str( OVSDB1Ip ) )
        response = main.OVSDB1.listPorts( "br-int" )
        if re.search( "vxlan", response ) and re.search( str( OVSDB2Ip ), response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="onos add default vxlan port on the node 1 sucess",
                                 onfail="onos add default vxlan port on the node 1 failed" )

        main.step( "Check default vxlan port on ovsdb node " + str( OVSDB2Ip ) )
        response = main.OVSDB2.listPorts( "br-int" )
        if re.search( "vxlan", response ) and re.search( str( OVSDB1Ip ), response ):
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="onos add default vxlan port on the node 2 sucess",
                                 onfail="onos add default vxlan port on the node 2 failed" )
