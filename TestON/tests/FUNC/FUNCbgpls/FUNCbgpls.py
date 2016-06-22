"""
**** Scripted by Antony Silvester  - antony.silvester@huawei.com ******


This Test check the bgp_ls functionality

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Discovery the topology using BGPLS
CASE3: Addition of new Node to existing topology
CASE4: Deletion of Node
Case5: Uninstalling the app


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
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        start cli sessions
        start BGPLS apps

        """

        import os
        main.log.info( "ONOS Single node start " +
                         "Scapy Tool - initialization" )
        main.case( "Setting up test environment" )
        main.caseExplanation = "Setup the test environment including " +\
                                "installing ONOS, start ONOS."


        PULLCODE = False
        if main.params[ 'GIT' ][ 'pull' ] == 'True':
            PULLCODE = True
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ipList = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        scapy_ip = os.getenv(main.params ['SCAPY'] ['HOSTNAMES'] )

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

        main.step( "Create cell file" )
        cellAppString = main.params[ 'ENV' ][ 'cellApps' ]

        main.ONOSbench.createCellFile( main.ONOSbench.ip_address, cellName,
                                       scapy_ip,
                                       cellAppString, ipList )

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )

        verifyResult = main.ONOSbench.verifyCell()

        # Make sure ONOS process is not running
        main.log.info( "Killing any ONOS processes" )
        killResults = main.TRUE
        for node in main.nodes:
            killed = main.ONOSbench.onosKill( node.ip_address )
            killResults = killResults and killed

        cleanInstallResult = main.TRUE
        gitPullResult = main.FALSE
        main.step( "Git checkout and pull" + gitBranch )
        if PULLCODE:
            main.ONOSbench.gitCheckout( gitBranch )
            gitPullResult = main.ONOSbench.gitPull()
            # values of 1 or 3 are good
            utilities.assert_lesser( expect=0, actual=gitPullResult,
                                      onpass="Git pull successful",
                                      onfail="Git pull failed" )

        #main.ONOSbench.getVersion( report=True )

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
        main.step( "Starting ONOS CLI sessions" )
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





    def CASE2( self, main ):
        """
        Discovery the topology using BGPLS
        """
        import os , sys
        import re
        import time

        main.case( "Testcase 2 : Discovery the Network Topology using BGPLS" )

        try:
            from tests.FUNC.FUNCbgpls.dependencies.Nbdata import BgpLs
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        bgplsConfig = BgpLs()
        Ne_id = bgplsConfig.Constants()
        app = bgplsConfig.apps()
        main.CLIs = []
        main.nodes = []
        main.numCtrls= 1


        ipList = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        scapy_ip = os.getenv(main.params ['SCAPY'] ['HOSTNAMES'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']
        bgplsConfig.ipValue(ipList,scapy_ip)

        for i in range( 1, main.numCtrls + 1 ):
            try:
                main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )
                main.nodes.append( getattr( main, 'ONOS' + str( i ) ) )
                ipList.append( main.nodes[ -1 ].ip_address )
            except AttributeError:
                break

        main.step( "Apply cell to environment" )
        bgplsConfig.Comments()

        bgplsConfig.Comments()
        main.log.info( "Sending BGPLS information " )
        bgplsConfig.Comments()


        main.Scapy1.handle.sendline( "sudo python  OnosSystemTest/TestON/tests/FUNC/FUNCbgpls/\
        dependencies/Scapyfiles/Topo_discovery.py" )
        bgplsConfig.Comments()
        main.log.info( "Enable BGPlS plugin in ONOS" )
        bgplsConfig.Comments()


        cliResults = main.ONOScli1.startOnosCli( main.nodes[0].ip_address)

        main.step( "Getting connected to ONOS" )
        utilities.assert_equals( expect=main.TRUE, actual=cliResults,
                                 onpass="ONOS cli startup successful",
                                 onfail="ONOS cli startup failed" )
        installResults = main.ONOScli1.activateApp( app[0])

        main.step( "Install onos-app-bgp" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-bgp successful",
                                 onfail="Install onos-app-bgp failed" )

        bgpls_post = bgplsConfig.DictoJson()

        bgplsConfig.Comments()
        main.log.info( "BGPLS RestConf input" )
        bgplsConfig.Comments()

        print (bgpls_post)
        main.ONOSrest.user_name = "karaf"
        main.ONOSrest.pwd = "karaf"
        Poststatus, result = main.ONOSrest.send( '/network/configuration/', method="POST", data=bgpls_post)
        main.step( "Configure BGP through RESTCONF" )

        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )


        bgplsConfig.Comments()
        main.log.info( "Check Network devices are Updated in ONOS " )
        bgplsConfig.Comments()
        time.sleep(15)

        response = main.ONOScli1.devices()
        main.step( "Check the nodes are discovered" )
        if response.find( Ne_id[1][0]) and response.find(Ne_id[1][1]) and response.find(Ne_id[1][2]) != -1:
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Node " + str( Ne_id[1][0]) + ( Ne_id[1][1]) + ( Ne_id[1][2]) + "  sucess",
                                 onfail="Node " + str( Ne_id[1][0]) + ( Ne_id[1][1]) + ( Ne_id[1][2]) + " failed" )


        bgplsConfig.Comments()
        main.log.info( "Kill Scapy process" )
        bgplsConfig.Comments()

        main.Scapy1.handle.sendline( "\x03" )
        time.sleep(90) #This Sleep time gives time for the socket to close.




    def CASE3( self, main ):
        """
        Addition of new Node to existing topology
        """
        import os , sys
        import re
        import time

        main.case( "Testcase 3: Addition of New Node to existing topology" )
        try:
            from tests.FUNC.FUNCbgpls.dependencies.Nbdata import BgpLs
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        bgplsConfig = BgpLs()
        Ne_id = bgplsConfig.Constants()
        app = bgplsConfig.apps()
        main.CLIs = []
        main.nodes = []
        main.numCtrls= 1


        ipList = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        scapy_ip = os.getenv( main.params ['SCAPY'] ['HOSTNAMES'] )
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        cellAppString= main.params[ 'ENV' ][ 'cellApps' ]
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        bgplsConfig.ipValue(ipList,scapy_ip)

        for i in range( 1, main.numCtrls + 1 ):
            try:
                main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )
                main.nodes.append( getattr( main, 'ONOS' + str( i ) ) )
                ipList.append( main.nodes[ -1 ].ip_address )
            except AttributeError:
                break

        bgplsConfig.Comments()
        main.log.info( "Sending BGPLS Packet " )
        bgplsConfig.Comments()

        main.Scapy1.handle.sendline( "sudo python  OnosSystemTest/TestON/tests/FUNC/FUNCbgpls/\
        dependencies/Scapyfiles/Update_Node.py" )
        bgplsConfig.Comments()
        main.log.info( "Enable BGPlS plugin in ONOS" )
        bgplsConfig.Comments()

        main.step( "UnInstall onos-app-bgp" )
        installResults = main.ONOScli1.deactivateApp( app[0] )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Uninstall  onos-app-bgp successful",
                                 onfail="Uninstall  onos-app-bgp failed" )

        installResults = main.ONOScli1.activateApp( app[0])
        main.step( "Install onos-app-bgp" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-bgp successful",
                                 onfail="Install onos-app-bgp failed" )


        bgpls_post = bgplsConfig.DictoJson()

        bgplsConfig.Comments()
        main.log.info( "BGPLS RestConf input" )
        bgplsConfig.Comments()

        bgplsConfig.Comments()
        main.log.info( "Check Network devices are Updated in ONOS " )
        bgplsConfig.Comments()
        time.sleep(120)

        response = main.ONOScli1.devices()
        main.step( "Check Newly added Node is getting updated" )

        if response.find( Ne_id[1][3]) != -1:
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Node " + str( Ne_id[1][3] ) + " update  sucess",
                                 onfail="Node " + str( Ne_id[1][3]) + " update failed" )
        bgplsConfig.Comments()
        main.log.info( "Kill Scapy process" )
        bgplsConfig.Comments()
        main.Scapy1.handle.sendline( "\x03" )



    def CASE4( self, main ):
        """
        Deletion of  Node
        """
        import os , sys
        import re
        import time
        main.case( "TestCase 4: Deletion of Node from existing Topology" )

        try:
            from tests.FUNC.FUNCbgpls.dependencies.Nbdata import BgpLs
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        bgplsConfig = BgpLs()
        Ne_id = bgplsConfig.Constants()
        app = bgplsConfig.apps()
        main.CLIs = []
        main.nodes = []
        main.numCtrls= 1

        bgplsConfig.Comments()
        main.log.info( "Blocked due to this defect : ONOS-3920 " )
        bgplsConfig.Comments()

        '''
        ipList = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        scapy_ip = os.getenv(main.params ['SCAPY'] ['HOSTNAMES'] )
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        cellAppString= main.params[ 'ENV' ][ 'cellApps' ]
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']
        bgplsConfig = BgpLs()
        bgplsConfig.ipValue(ipList,scapy_ip)

        main.ONOSbench.createCellFile( main.ONOSbench.ip_address, cellName,
                                       scapy_ip,
                                       cellAppString, ipList , onosUser="karaf" )

        for i in range( 1, main.numCtrls + 1 ):
            try:
                main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )
                main.nodes.append( getattr( main, 'ONOS' + str( i ) ) )
                ipList.append( main.nodes[ -1 ].ip_address )
            except AttributeError:
                break

        main.step( "Apply cell to environment" )
        bgplsConfig.Comments()
        cellResult = main.ONOSbench.setCell( cellName )

        bgplsConfig.Comments()
        main.log.info( "Sending BGPLS information " )
        bgplsConfig.Comments()


        main.Scapy1.handle.sendline( "sudo python  OnosSystemTest/TestON/tests/FUNC/FUNCbgpls/dependencies/Scapyfiles/Deletion_Node.py" )
        #main.Scapy1.handle.expect( "sdn:" )
        #main.Scapy1.handle.sendline( "rocks" )


        bgplsConfig.Comments()
        main.log.info( "Enable BGPlS plugin in ONOS" )
        bgplsConfig.Comments()


        cliResults = main.ONOScli1.startOnosCli( main.nodes[0].ip_address)

        main.step( "Getting connected to ONOS" )
        utilities.assert_equals( expect=main.TRUE, actual=cliResults,
                                 onpass="ONOS cli startup successful",
                                 onfail="ONOS cli startup failed" )
        installResults = main.ONOScli1.activateApp( app[0])

        main.step( "Install onos-app-bgp" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-bgp successful",
                                 onfail="Install onos-app-bgp failed" )

        main.step( "Install onos-app-bgpflow" )
        installResults = main.ONOScli1.activateApp( app[1] )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Install onos-app-bgpflow successful",
                                 onfail="Install onos-app-bgpflow failed" )


        bgpls_post = bgplsConfig.DictoJson()

        bgplsConfig.Comments()
        main.log.info( "BGPLS RestConf input" )
        bgplsConfig.Comments()

        print (bgpls_post)
        main.ONOSrest.user_name = "karaf"
        main.ONOSrest.pwd = "karaf"
        Poststatus, result = main.ONOSrest.send( ipList,httpport,'', path + 'v1/network/configuration/',
                                                 'POST', None, bgpls_post, debug=True )

        main.step( "Configure BGP through RESTCONF" )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )


        bgplsConfig.Comments()
        main.log.info( "Check Network devices is deleted from  ONOS " )
        bgplsConfig.Comments()
        time.sleep(15)

        response = main.ONOScli1.devices()

        main.step( "Check whehther Node is deleted successfully" )

        if response.find(Ne_id[3]) != -1:
            stepResult = main.TRUE
        else:
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.FALSE,
                                 actual=stepResult,
                                 onpass="Node " + str( Ne_id[3] ) + " Deletion sucess",
                                 onfail="Node " + str( Ne_id[3] ) + " Deletion  failed" )

        bgplsConfig.Comments()
        main.log.info( "Kill Scapy process" )
        bgplsConfig.Comments()

        main.Scapy1.handle.sendline( "\x03" )
        '''


    def CASE5( self, main ):
        """
        Uninstalling the app
        """
        import os,sys
        import re
        import time

        main.case( "TestCase 5: UnInstalling of app" )
        try:
            from tests.FUNC.FUNCbgpls.dependencies.Nbdata import BgpLs
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        bgplsConfig = BgpLs()
        app = bgplsConfig.apps()
        main.CLIs = []
        main.nodes = []
        main.numCtrls= 1


        ipList = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        scapy_ip = os.getenv(main.params ['SCAPY'] ['HOSTNAMES'] )
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        cellAppString= main.params[ 'ENV' ][ 'cellApps' ]

        bgplsConfig = BgpLs()
        bgplsConfig.ipValue(ipList,scapy_ip)
        main.ONOSbench.createCellFile( main.ONOSbench.ip_address, cellName,
                                       scapy_ip,
                                       cellAppString, ipList , onosUser="karaf" )

        for i in range( 1, main.numCtrls + 1 ):
            try:
                main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )
                main.nodes.append( getattr( main, 'ONOS' + str( i ) ) )
                ipList.append( main.nodes[ -1 ].ip_address )
            except AttributeError:
                break

        main.step( "Apply cell to environment" )
        bgplsConfig.Comments()
        cellResult = main.ONOSbench.setCell( cellName )

        bgplsConfig.Comments()
        main.log.info( "Logging into ONOS CLI " )
        bgplsConfig.Comments()

        cliResults = main.ONOScli1.startOnosCli( main.nodes[0].ip_address )
        utilities.assert_equals( expect=main.TRUE, actual=cliResults,
                                 onpass="ONOS cli startup successful",
                                 onfail="ONOS cli startup failed" )

        bgplsConfig.Comments()
        main.log.info( "Uninstall onos-app-bgp" )
        bgplsConfig.Comments()
        main.step( "UnInstall onos-app-bgp" )
        installResults = main.ONOScli1.deactivateApp( app[0] )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass="Uninstall  onos-app-bgp successful",
                                 onfail="Uninstall  onos-app-bgp failed" )



