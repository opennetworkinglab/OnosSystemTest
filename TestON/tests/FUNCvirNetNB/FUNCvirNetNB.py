"""
Description: This test is to determine if North bound
    can handle the request

List of test cases:
CASE1 - Variable initialization and optional pull and build ONOS package
CASE2 - Create Network northbound test
CASE3 - Update Network northbound test
CASE4 - Delete Network northbound test
CASE5 - Create Subnet northbound test
CASE6 - Update Subnet northbound test
CASE7 - Delete Subnet northbound test
CASE8 - Create Virtualport northbound test
CASE9 - Update Virtualport northbound test
CASE10 - Delete Virtualport northbound test
CASE11 - Post Error Json Create Network test
CASE12 - Post Error Json Create Subnet test
CASE13 - Post Error Json Create Virtualport test

lanqinglong@huawei.com
"""
import os

class FUNCvirNetNB:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        CASE1 is to compile ONOS and push it to the test machines

        Startup sequence:
        cell<name>
        onos-verify-cell
        NOTE:temporary - onos-remove-raft-logs
        onos-uninstall
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        start cli sessions
        start vtnrsc
        """

        import time
        import os
        main.log.info( "ONOS Single node Start "+
                      "VirtualNet Northbound test - initialization" )
        main.case( "Setting up test environment" )
        main.caseExplanation  = "Setup the test environment including "+\
                                "installing ONOS,start ONOS."

        # load some variables from the params file
        PULLCODE = False
        if main.params['GIT']['pull'] =='True':
            PULLCODE = True
        gitBranch = main.params['GIT']['branch']
        cellName = main.params['ENV']['cellName']
        ipList = os.getenv( main.params['CTRL']['ip1'] )

        main.step("Create cell file and apply to environment")
        cellAppString = main.params['ENV']['cellApps']
        main.ONOSbench.createCellFile(main.ONOSbench.ip_address,cellName,
                                      main.Mininet1.ip_address,
                                      cellAppString,ipList )

        cellResult = main.ONOSbench.setCell(cellName)
        verifyResult = main.ONOSbench.verifyCell()

        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + \
                                        "environment",
                                 onfail="Failed to apply cell to environment " )

        #FIXME:this is short term fix
        main.log.info( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()

        main.CLIs = []
        main.nodes = []
        main.numCtrls=1
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )

        for i in range ( 1, main.numCtrls +1):
            try:
                main.CLIs.append( getattr( main, 'ONOScli' + str(i) ) )
                main.nodes.append( getattr( main, 'ONOS' + str(i) ) )
                ipList.append( main.nodes[ -1 ].ip_address )
            except AttributeError:
                break

        main.log.info( "Uninstalling ONOS" )
        for node in main.nodes:
            main.ONOSbench.onosUninstall( node.ip_address )

        #Make sure ONOS is DEAD
        main.log.info( "Killing any ONOS processes" )
        killResults = main.TRUE
        for node in main.nodes:
            killed = main.ONOSbench.onosKill( node.ip_address )
            killResults = killResults and killed

        cleanInstallResult = main.TRUE
        gitPullResult = main.TRUE
        main.log.info( "Git checkout and pull " + gitBranch )
        if PULLCODE:
            main.ONOSbench.gitCheckout ( gitBranch )
            gitPullResult = main.ONOSbench.gitPull()
            # values of 1 or 3 are good
            utilities.assert_lesser ( expect=0, actual=gitPullResult,
                                      onpass="Git pull successful",
                                      onfail ="Git pull failed" )
        main.ONOSbench.getVersion( report =True )
        main.step( "Using mvn clean install" )
        cleanInstallResult= main.TRUE
        if PULLCODE and gitPullResult == main.TRUE:
            cleanInstallResult = main.ONOSbench.cleanInstall()
        else:
            main.log.warn("Did not pull new code so skipping mvn "+
                          "clean install")

        utilities.assert_equals( expect=main.TRUE,
                                 actual=cleanInstallResult,
                                 onpass="MCI successful",
                                 onfail="MCI failed" )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=packageResult,
                                 onpass="Successfully created ONOS package",
                                 onfail="Failed to create ONOS package " )
        time.sleep( main.startUpSleep )

        main.step( "Installing ONOS package" )
        onosInstallResult = main.ONOSbench.onosInstall(
            options="-f",node=main.nodes[0].ip_address )
        utilities.assert_equals( expect=main.TRUE, actual=onosInstallResult,
                                onpass="ONOS install successful",
                                onfail="ONOS install failed" )
        time.sleep( main.startUpSleep )

        main.step( "Checking if ONOS is up yet" )

        for i in range( 2 ):
            onos1Isup =  main.ONOSbench.isup( main.nodes[0].ip_address )
            if onos1Isup:
                break
        utilities.assert_equals( expect=main.TRUE, actual=onos1Isup,
                     onpass="ONOS startup successful",
                     onfail="ONOS startup failed" )
        time.sleep( main.startUpSleep )

        main.log.step( "Starting ONOS CLI sessions" )

        print main.nodes[0].ip_address
        cliResults = main.ONOScli1.startOnosCli(main.nodes[0].ip_address)
        utilities.assert_equals( expect=main.TRUE, actual=cliResults,
                                onpass="ONOS cli startup successful",
                                onfail="ONOS cli startup failed" )
        time.sleep( main.startUpSleep )

        main.step( "App Ids check" )
        appCheck = main.ONOScli1.appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[0].apps() )
            main.log.warn( main.CLIs[0].appIDs() )
        utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                     onpass="App Ids seem to be correct",
                     onfail="Something is wrong with app Ids" )

        if cliResults == main.FALSE:
            main.log.error( "Failed to start ONOS, stopping test" )
            main.cleanup()
            main.exit()

        main.step( "Install org.onosproject.vtn app" )
        installResults = main.ONOScli1.activateApp( "org.onosproject.vtn" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                     onpass="Install org.onosproject.vtn successful",
                     onfail="Install org.onosproject.vtn app failed" )

        time.sleep( main.startUpSleep )

    def CASE2 ( self,main ):

        """
        Test Post Network
        """
        import os

        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Network Post test Start" )
        main.case( "Virtual Network NBI Test - Network" )
        main.caseExplanation  = "Test Network Post NBI " +\
                                "Verify Post Data same with Stored Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        postdata = network.DictoJson()

        main.step( "Post Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path+'networks/',
                                                'POST', None, postdata)

        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Success",
                onfail="Post Failed " + str( Poststatus ) + str( result ) )

        main.step( "Get Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, port, network.id, path+'networks/',
                                                'GET', None, None)
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get Success",
                onfail="Get Failed " + str( Getstatus ) + str( result ) )

        main.log.info("Post Network Data is :%s\nGet Network Data is:%s"%(postdata,result))

        main.step( "Compare Send Id and Get Id" )
        IDcmpresult = network.JsonCompare( postdata, result, 'network', 'id' )
        TanantIDcmpresult = network.JsonCompare( postdata, result, 'network', 'tenant_id' )
        Cmpresult = IDcmpresult and TanantIDcmpresult

        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:ID compare: " + str( IDcmpresult ) + \
                       ",Tenant id compare :" + str( TanantIDcmpresult ) )

        deletestatus,result = main.ONOSrest.send( ctrlip, port, network.id, path+'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed")

        if Cmpresult != True:
            main.log.error( "Post Network compare failed" )

    def CASE3( self,main ):

        """
        Test Update Network
        """
        import os

        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Network Update test Start" )
        main.case( "Virtual Network NBI Test - Network" )
        main.caseExplanation  = "Test Network Update NBI " +\
                                "Verify Update Data same with Stored Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        network.shared = False
        postdata = network.DictoJson()

        network.shared = True
        postdatanew = network.DictoJson()

        main.step( "Post Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path+'networks',
                                                 'POST', None, postdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Success",
                onfail="Post Failed " + str( Poststatus ) + str( result ) )

        main.step( "Update Data via HTTP" )
        Updatestatus, result = main.ONOSrest.send( ctrlip, port, network.id, path+'networks/',
                                                   'PUT', None, postdatanew)
        utilities.assert_equals(
                expect='200',
                actual=Updatestatus,
                onpass="Update Success",
                onfail="Update Failed " + str( Updatestatus ) + str( result ) )

        main.step( "Get Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, port, network.id, path+'networks/',
                                                'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get Success",
                onfail="Get Failed " + str( Getstatus ) + str( result ) )

        main.step( "Compare Update data." )
        IDcmpresult = network.JsonCompare( postdatanew, result, 'network', 'id' )
        TanantIDcmpresult = network.JsonCompare( postdatanew, result, 'network', 'tenant_id' )
        Shareresult = network.JsonCompare( postdatanew, result, 'network', 'shared' )

        Cmpresult = IDcmpresult and TanantIDcmpresult and Shareresult
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:ID compare:" + str( IDcmpresult ) + \
                       ",Tenant id compare:"+ str( TanantIDcmpresult ) + \
                       ",Name compare:" + str( Shareresult ) )

        deletestatus,result = main.ONOSrest.send( ctrlip, port, network.id, path+'networks/',
                                                 'DELETE', None, None )

        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )

        if Cmpresult != True:
            main.log.error( "Update Network compare failed" )

    def CASE4( self,main ):

        """
        Test Delete Network
        """
        import os

        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Network Delete test Start" )
        main.case( "Virtual Network NBI Test - Network" )
        main.caseExplanation = "Test Network Delete NBI " +\
                                "Verify Stored Data is NULL after Delete"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        postdata = network.DictoJson()

        main.step( "Post Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'networks/',
                                                 'POST', None, postdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Success",
                onfail="Post Failed " + str( Poststatus ) + str( result ) )

        main.step( "Delete Data via HTTP" )
        Deletestatus, result = main.ONOSrest.send( ctrlip, port, network.id, path+'networks/',
                                                'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Deletestatus,
                onpass="Delete Success",
                onfail="Delete Failed " + str( Deletestatus ) + str( result ) )

        main.step( "Get Data is NULL" )
        Getstatus, result = main.ONOSrest.send( ctrlip, port, network.id, path+'networks/',
                                                'GET', None, None )
        utilities.assert_equals(
                expect='Network is not found',
                actual=result,
                onpass="Get Success",
                onfail="Get Failed " + str( Getstatus ) + str( result ) )

        if result != 'Network is not found':
            main.log.error( "Delete Network failed" )

    def CASE5( self, main ):

        """
        Test Post Subnet
        """
        import os

        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNB.dependencies.Nbdata import SubnetData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Subnet Post test Start" )
        main.case( "Virtual Network NBI Test - Subnet" )
        main.caseExplanation = "Test Subnet Post NBI " +\
                                "Verify Stored Data is same with Post Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        subnet = SubnetData()
        subnet.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id

        networkpostdata = network.DictoJson()
        subnetpostdata = subnet.DictoJson()

        main.step( "Post Network Data via HTTP(Post Subnet need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Get Subnet Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, port, subnet.id, path + 'subnets/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get Subnet Success",
                onfail="Get Subnet Failed " + str( Getstatus ) + "," + str( result ) )

        IDcmpresult = subnet.JsonCompare( subnetpostdata, result, 'subnet', 'id' )
        TanantIDcmpresult = subnet.JsonCompare( subnetpostdata, result, 'subnet', 'tenant_id' )
        NetoworkIDcmpresult = subnet.JsonCompare( subnetpostdata, result, 'subnet', 'network_id' )

        main.step( "Compare Post Subnet Data via HTTP" )
        Cmpresult = IDcmpresult and TanantIDcmpresult and NetoworkIDcmpresult
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:ID compare:" + str( IDcmpresult ) + \
                       ",Tenant id compare:"+ str( TanantIDcmpresult ) + \
                       ",Network id compare:" + str( NetoworkIDcmpresult ) )

        deletestatus,result = main.ONOSrest.send( ctrlip, port, network.id, path+'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )

        if Cmpresult != True:
            main.log.error( "Post Subnet compare failed" )

    def CASE6( self, main ):

        """
        Test Post Subnet
        """
        import os

        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNB.dependencies.Nbdata import SubnetData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Subnet Update test Start" )
        main.case( "Virtual Network NBI Test - Subnet" )
        main.caseExplanation = "Test Subnet Update NBI " +\
                                "Verify Stored Data is same with Update Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        subnet = SubnetData()
        subnet.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        subnet.start = "192.168.2.1"
        subnet.end = "192.168.2.255"
        networkpostdata = network.DictoJson()
        subnetpostdata = subnet.DictoJson()

        #Change allocation_poolsdata scope
        subnet.start = "192.168.102.1"
        subnet.end = "192.168.102.255"
        #end change
        newsubnetpostdata = subnet.DictoJson()

        main.step( "Post Network Data via HTTP(Post Subnet need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Update Subnet Data via HTTP" )
        Putstatus, result = main.ONOSrest.send( ctrlip, port, subnet.id, path + 'subnets/',
                                                 'PUT', None, newsubnetpostdata )
        utilities.assert_equals(
                expect='203',
                actual=Putstatus,
                onpass="Update Subnet Success",
                onfail="Update Subnet Failed " + str( Putstatus ) + "," + str( result ) )

        main.step( "Get Subnet Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, port, subnet.id, path + 'subnets/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get Subnet Success",
                onfail="Get Subnet Failed " + str( Getstatus ) + "," + str( result ) )

        IDcmpresult = subnet.JsonCompare( newsubnetpostdata, result, 'subnet', 'id' )
        TanantIDcmpresult = subnet.JsonCompare( newsubnetpostdata, result, 'subnet', 'tenant_id' )
        Poolcmpresult = subnet.JsonCompare( newsubnetpostdata, result, 'subnet', 'allocation_pools' )

        main.step( "Compare Subnet Data" )
        Cmpresult = IDcmpresult and TanantIDcmpresult and Poolcmpresult
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:ID compare:" + str( IDcmpresult ) + \
                       ",Tenant id compare:"+ str( TanantIDcmpresult ) + \
                       ",Pool compare:" + str( Poolcmpresult ) )

        main.step( "Delete Subnet via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, port, network.id, path+'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )

        if Cmpresult != True:
            main.log.error( "Update Subnet compare failed" )

    def CASE7( self, main ):

        """
        Test Delete Subnet
        """
        import os

        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNB.dependencies.Nbdata import SubnetData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Subnet Delete test Start" )
        main.case( "Virtual Network NBI Test - Subnet" )
        main.caseExplanation = "Test Subnet Delete NBI " +\
                                "Verify Stored Data is Null after Delete"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        subnet = SubnetData()
        subnet.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id

        networkpostdata = network.DictoJson()
        subnetpostdata = subnet.DictoJson()

        main.step( "Post Network Data via HTTP(Post Subnet need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Delete Subnet Data via HTTP" )
        Deletestatus, result = main.ONOSrest.send( ctrlip, port, subnet.id, path + 'subnets/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='201',
                actual=Deletestatus,
                onpass="Delete Subnet Success",
                onfail="Delete Subnet Failed " + str( Deletestatus ) + "," + str( result ) )

        main.step( "Get Subnet Data is NULL" )
        Getstatus, result = main.ONOSrest.send( ctrlip, port, subnet.id, path + 'subnets/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='Subnet is not found',
                actual=result,
                onpass="Get Subnet Success",
                onfail="Get Subnet Failed " + str( Getstatus ) + str( result ) )

        if result != 'Subnet is not found':
            main.log.error( "Delete Subnet failed" )

    def CASE8( self, main ):

        """
        Test Post Port
        """
        import os

        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNB.dependencies.Nbdata import SubnetData
            from tests.FUNCvirNetNB.dependencies.Nbdata import VirtualPortData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Port Post test Start" )
        main.case( "Virtual Network NBI Test - Port" )
        main.caseExplanation = "Test Port Post NBI " +\
                                "Verify Stored Data is same with Post Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        subnet = SubnetData()
        subnet.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        port = VirtualPortData()
        port.id = "9352e05c-58b8-4f2c-b4df-c20435ser56466"
        port.subnet_id = subnet.id
        port.tenant_id = network.tenant_id
        port.network_id = network.id

        networkpostdata = network.DictoJson()
        subnetpostdata = subnet.DictoJson()
        portpostdata = port.DictoJson()

        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, portpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Get Port Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, httpport, port.id, path + 'ports/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get Port Success",
                onfail="Get Port Failed " + str( Getstatus ) + "," + str( result ) )

        main.step( "Compare Post Port Data" )
        IDcmpresult = subnet.JsonCompare( portpostdata, result, 'port', 'id' )
        TanantIDcmpresult = subnet.JsonCompare( portpostdata, result, 'port', 'tenant_id' )
        NetoworkIDcmpresult = subnet.JsonCompare( portpostdata, result, 'port', 'network_id' )
        fixedIpresult = subnet.JsonCompare( portpostdata, result, 'port', 'fixed_ips' )

        Cmpresult = IDcmpresult and TanantIDcmpresult and NetoworkIDcmpresult and fixedIpresult
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:ID compare:" + str( IDcmpresult ) + \
                       ",Tenant id compare:"+ str( TanantIDcmpresult ) + \
                       ",Network id compare:" + str( NetoworkIDcmpresult ) +\
                       ",FixIp compare:" + str( fixedIpresult ) )

        main.step( "Clean Data via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, network.id, path + 'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )

        if Cmpresult != True:
            main.log.error( "Post port compare failed" )

    def CASE9( self, main ):

        """
        Test Update Port
        """
        import os

        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNB.dependencies.Nbdata import SubnetData
            from tests.FUNCvirNetNB.dependencies.Nbdata import VirtualPortData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Port Update test Start" )
        main.case( "Virtual Network NBI Test - Port" )
        main.caseExplanation = "Test Port Update NBI " +\
                                "Verify Stored Data is same with New Post Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        subnet = SubnetData()
        subnet.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        port = VirtualPortData()
        port.id = "9352e05c-58b8-4f2c-b4df-c20435ser56466"
        port.subnet_id = subnet.id
        port.tenant_id = network.tenant_id
        port.network_id = network.id
        port.name = "onos"

        networkpostdata = network.DictoJson()
        subnetpostdata = subnet.DictoJson()
        portpostdata = port.DictoJson()

        #create update data
        port.name = "onos-new"
        newportpostdata = port.DictoJson()
        #end

        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, portpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Update Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, port.id, path + 'ports/',
                                                 'PUT', None, newportpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Update Port Success",
                onfail="Update Port Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Get Port Data via HTTP" )
        Getstatus, result = main.ONOSrest.send( ctrlip, httpport, port.id, path + 'ports/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Getstatus,
                onpass="Get Port Success",
                onfail="Get Port Failed " + str( Getstatus ) + "," + str( result ) )

        main.step( "Compare Update Port Data" )
        IDcmpresult = subnet.JsonCompare( portpostdata, result, 'port', 'id' )
        TanantIDcmpresult = subnet.JsonCompare( portpostdata, result, 'port', 'tenant_id' )
        NetoworkIDcmpresult = subnet.JsonCompare( portpostdata, result, 'port', 'network_id' )
        Nameresult = subnet.JsonCompare( newportpostdata, result, 'port', 'name' )

        Cmpresult = IDcmpresult and TanantIDcmpresult and NetoworkIDcmpresult and Nameresult
        utilities.assert_equals(
                expect=True,
                actual=Cmpresult,
                onpass="Compare Success",
                onfail="Compare Failed:ID compare:" + str( IDcmpresult ) + \
                       ",Tenant id compare:"+ str( TanantIDcmpresult ) + \
                       ",Network id compare:" + str( NetoworkIDcmpresult ) + \
                       ",Name compare:" + str(Nameresult) )

        main.step( "Clean Data via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, network.id, path + 'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )

        if Cmpresult != True:
            main.log.error( "Update port compare failed" )

    def CASE10( self, main ):

        """
        Test Delete Port
        """
        import os

        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNB.dependencies.Nbdata import SubnetData
            from tests.FUNCvirNetNB.dependencies.Nbdata import VirtualPortData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Port Delete test Start" )
        main.case( "Virtual Network NBI Test - Port" )
        main.caseExplanation = "Test Port Delete NBI " +\
                                "Verify port delete success"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.log.info( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        subnet = SubnetData()
        subnet.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        port = VirtualPortData()
        port.id = "9352e05c-58b8-4f2c-b4df-c20435ser56466"
        port.subnet_id = subnet.id
        port.tenant_id = network.tenant_id
        port.network_id = network.id

        networkpostdata = network.DictoJson()
        subnetpostdata = subnet.DictoJson()
        portpostdata = port.DictoJson()

        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, portpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Port Success",
                onfail="Post Port Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Delete Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, port.id, path + 'ports/',
                                                 'Delete', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Delete Port Success",
                onfail="Delete Port Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Get Port Data is NULL" )
        Getstatus, result = main.ONOSrest.send( ctrlip, httpport, port.id, path + 'ports/',
                                                 'GET', None, None )
        utilities.assert_equals(
                expect='VirtualPort is not found',
                actual=result,
                onpass="Get Port Success",
                onfail="Get Port Failed " + str( Getstatus ) + "," + str( result ) )

        if result != 'VirtualPort is not found':
            main.log.error( "Delete Port failed" )

        main.step( "Clean Data via HTTP" )
        deletestatus,result = main.ONOSrest.send( ctrlip, httpport, network.id, path + 'networks/',
                                                 'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=deletestatus,
                onpass="Delete Network Success",
                onfail="Delete Network Failed" )            
    def CASE11 ( self,main ):

        """
        Test Post Error Json Create Network
        """
        import os

        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Post Error Json Create Network test Start" )
        main.case( "Virtual Network NBI Test - Network" )
        main.caseExplanation  = "Test Network Post With Error json " +\
                                "The wrong Json can't post network successfully"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.step( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        #The network.admin_state_up should be True or False,when the admin_state_up is 'tttttttttt',the Json can't post.
        network.admin_state_up = 'tttttttttt'
        #The network.routerExternal should be True or False,when the routerExternal is 'ffffffffffff',the Json can't post.
        network.routerExternal = 'ffffffffffff'
        #The network.shared should be True or False,when the shared is 'ffffffffffffff',the Json can't post.
        network.shared = 'ffffffffffffff'
        postdata = network.DictoJson()

        main.step( "Post Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path+'networks/',
                                                'POST', None, postdata)

        utilities.assert_equals(
                expect='500',
                actual=Poststatus,
                onpass="The Json is wrong,can't post",
                onfail="Wrong Json can post successfully " )
    def CASE12( self, main ):

        """
        Test Post Error Json Create Subnet
        """
        import os

        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNB.dependencies.Nbdata import SubnetData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Post Error Json Create Subnet test Start" )
        main.case( "Virtual Network NBI Test - Subnet" )
        main.caseExplanation = "Test Subnet Post With Error json " +\
                                "The wrong Json can't post network successfully"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.step( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        subnet = SubnetData()
        subnet.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        #The subnet.enable_dhcp should be True or False,when the enable_dhcp is 'tttttttttttttt',the Json can't post.
        subnet.enable_dhcp = 'tttttttttttttt'
        #The subnet.tenant_id should be True or False,when the tenant_id is ffffffffffffff',the Json can't post.
        subnet.shared = 'ffffffffffffff'
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id

        networkpostdata = network.DictoJson()
        subnetpostdata = subnet.DictoJson()

        main.step( "Post Network Data via HTTP(Post Subnet need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='500',
                actual=Poststatus,
                onpass="The Json is wrong,can't post",
                onfail="Wrong Json can post successfully " )
    def CASE13( self, main ):

        """
        Test Post Error Json Create Virtualport
        """
        import os

        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
            from tests.FUNCvirNetNB.dependencies.Nbdata import SubnetData
            from tests.FUNCvirNetNB.dependencies.Nbdata import VirtualPortData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error, please check!" )
            main.cleanup()
            main.exit()

        main.log.info( "ONOS Post Error Json Create Subnet test Start" )
        main.case( "Virtual Network NBI Test - Port" )
        main.caseExplanation = "Test Subnet Post With Error json " +\
                                "The wrong Json can't create port successfully"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        httpport = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.step( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        subnet = SubnetData()
        subnet.id = "e44bd655-e22c-4aeb-b1e9-ea1606875178"
        subnet.tenant_id = network.tenant_id
        subnet.network_id = network.id
        port = VirtualPortData()
        port.id = "9352e05c-58b8-4f2c-b4df-c20435ser56466"
        port.subnet_id = subnet.id
        port.tenant_id = network.tenant_id
        port.network_id = network.id
        #The port.adminStateUp should be True or False,when the adminStateUp is 'tttttttttttt',the Json can't post.
        port.adminStateUp = 'tttttttttttt'

        networkpostdata = network.DictoJson()
        subnetpostdata = subnet.DictoJson()
        portpostdata = port.DictoJson()

        main.step( "Post Network Data via HTTP(Post port need post network)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'networks/',
                                                 'POST', None, networkpostdata )
        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Network Success",
                onfail="Post Network Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Subnet Data via HTTP(Post port need post subnet)" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'subnets/',
                                                 'POST', None, subnetpostdata )
        utilities.assert_equals(
                expect='202',
                actual=Poststatus,
                onpass="Post Subnet Success",
                onfail="Post Subnet Failed " + str( Poststatus ) + "," + str( result ) )

        main.step( "Post Port Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, httpport, '', path + 'ports/',
                                                 'POST', None, portpostdata )
        utilities.assert_equals(
                expect='500',
                actual=Poststatus,
                onpass="The Json is wrong,can't post",
                onfail="Wrong Json can post successfully" )
