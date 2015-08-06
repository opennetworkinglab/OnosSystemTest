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

        main.step("Create cell file")
        cellAppString = main.params['ENV']['cellApps']
        main.ONOSbench.createCellFile(main.ONOSbench.ip_address,cellName,
                                      main.Mininet1.ip_address,
                                      cellAppString,ipList )

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell(cellName)
        verifyResult = main.ONOSbench.verifyCell()

        #FIXME:this is short term fix
        main.log.info( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftlogs()

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
        main.step( "Git checkout and pull " + gitBranch )
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

        main.step( "Install onos-app-vtnrsc app" )
        installResults = main.ONOScli1.featureInstall( "onos-app-vtnrsc" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                     onpass="Install onos-app-vtnrsc successful",
                     onfail="Install onos-app-vtnrsc app failed" )

        time.sleep( main.startUpSleep )
        
        main.step( "Install onos-app-vtnweb app" )
        installResults = main.ONOScli1.featureInstall( "onos-app-vtnweb" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                     onpass="Install onos-app-vtnweb successful",
                     onfail="Install onos-app-vtnweb app failed" )

        time.sleep( main.startUpSleep )

    def CASE2 ( self,main ):

        """
        Test Post Network
        """
        import os,sys
        sys.path.append("..")
        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error,please check!" )

        main.log.info( "ONOS Network Post test Start" )
        main.case( "Virtual Network NBI Test - Network" )
        main.caseExplanation  = "Test Network Post NBI " +\
                                "Verify Post Data same with Stored Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.step( "Generate Post Data" )
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

        if Cmpresult !=True:
            main.log.error( "Post Network compare failed" )

    def CASE3( self,main ):

        """
        Test Update Network
        """
        import os,sys
        sys.path.append("..")
        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error,please check!" )

        main.log.info( "ONOS Network Update test Start" )
        main.case( "Virtual Network NBI Test - Network" )
        main.caseExplanation  = "Test Network Update NBI " +\
                                "Verify Update Data same with Stored Data"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.step( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        network.shared = 'false'
        postdata = network.DictoJson()

        network.shared = 'true'
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

        if Cmpresult!=True:
            main.log.error( "Update Network compare failed" )

    def CASE4( self,main ):

        """
        Test Delete Network
        """
        import os,sys
        sys.path.append("..")
        try:
            from tests.FUNCvirNetNB.dependencies.Nbdata import NetworkData
        except ImportError:
            main.log.exception( "Something wrong with import file or code error." )
            main.log.info( "Import Error,please check!" )

        main.log.info( "ONOS Network Delete test Start" )
        main.case( "Virtual Network NBI Test - Network" )
        main.caseExplanation = "Test Network Delete NBI " +\
                                "Verify Stored Data is NULL after Delete"

        ctrlip = os.getenv( main.params['CTRL']['ip1'] )
        port = main.params['HTTP']['port']
        path = main.params['HTTP']['path']

        main.step( "Generate Post Data" )
        network = NetworkData()
        network.id = '030d6d3d-fa36-45bf-ae2b-4f4bc43a54dc'
        network.tenant_id = '26cd996094344a0598b0a1af1d525cdc'
        postdata = network.DictoJson()

        main.step( "Post Data via HTTP" )
        Poststatus, result = main.ONOSrest.send( ctrlip, port , '' , path + 'networks/',
                                                 'POST', None , postdata )

        utilities.assert_equals(
                expect='200',
                actual=Poststatus,
                onpass="Post Success",
                onfail="Post Failed " + str( Poststatus ) + str( result ) )

        main.step( "Delete Data via HTTP" )
        Deletestatus, result = main.ONOSrest.send( ctrlip,port,network.id,path+'networks/',
                                                'DELETE', None, None )
        utilities.assert_equals(
                expect='200',
                actual=Deletestatus,
                onpass="Delete Success",
                onfail="Delete Failed " + str( Getstatus ) + str( result ) )

        main.step( "Get Data is NULL" )
        Getstatus, result = main.ONOSrest.send( ctrlip, port, network.id, path+'networks/',
                                                'GET', None, None )
        utilities.assert_equals(
                expect='The tenantNetwork does not exists',
                actual=result,
                onpass="Get Success",
                onfail="Get Failed " + str( Getstatus ) + str( result ) )

        if result != 'The tenantNetwork does not exists':
            main.log.error( "Delete Network failed" )
