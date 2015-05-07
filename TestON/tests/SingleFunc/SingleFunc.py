
# Testing the basic functionality of ONOS Next
# For sanity and driver functionality excercises only.

import time
import json

time.sleep( 1 )

class SingleFunc:

    def __init__( self ):
        self.default = ''

    def CASE10( self, main ):
        import time
        import os
        """
        Startup sequence:
        cell <name>
        onos-verify-cell
        onos-remove-raft-log
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        """
        #Local variables
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        main.ONOS1ip = os.environ[ 'OC1' ]
        main.ONOS1port = main.params[ 'CTRL' ][ 'port1' ]
        main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        topology = main.params[ 'MININET' ][ 'topo' ]
        PULLCODE = False
        if main.params[ 'GIT' ][ 'pull' ] == 'True':
            PULLCODE = True
        main.case( "Setting up test environment" )

        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + \
                                        "environment",
                                 onfail="Failed to apply cell to environment " )
        """main.step( "Removing raft logs" )
        removeRaftResult = main.ONOSbench.onosRemoveRaftLogs()
        stepResult = removeRaftResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully removed raft logs",
                                 onfail="Failed to remove raft logs" )
        """
        if PULLCODE:
            main.step( "Git checkout and pull " + gitBranch )
            main.ONOSbench.gitCheckout( gitBranch )
            gitPullResult = main.ONOSbench.gitPull()
            if gitPullResult == main.ERROR:
                main.log.error( "Error pulling git branch" )
            main.step( "Using mvn clean & install" )
            cleanInstallResult = main.ONOSbench.cleanInstall()
            stepResult = cleanInstallResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully compiled latest ONOS",
                                     onfail="Failed to compile latest ONOS" )
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        stepResult = packageResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully created ONOS package",
                                 onfail="Failed to create ONOS package" )

        main.step( "Uninstalling ONOS package" )
        onosUninstallResult = main.ONOSbench.onosUninstall(
                                                          nodeIp=main.ONOS1ip )
        stepResult = onosUninstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully uninstalled ONOS package",
                                 onfail="Failed to uninstall ONOS package" )
        time.sleep( 5 )
        main.step( "Installing ONOS package" )
        onosInstallResult = main.ONOSbench.onosInstall( node=main.ONOS1ip )
        stepResult = onosInstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )

        main.step( "Starting ONOS service" )
        stopResult = main.TRUE
        startResult = main.TRUE
        onosIsUp = main.ONOSbench.isup()
        if onosIsUp == main.TRUE:
            main.log.report( "ONOS instance is up and ready" )
        else:
            main.log.report( "ONOS instance may not be up, stop and " +
                             "start ONOS again " )
            stopResult = main.ONOSbench.onosStop( main.ONOS1ip )
            startResult = main.ONOSbench.onosStart( main.ONOS1ip )
        stepResult = onosIsUp and stopResult and startResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ONOS service is ready",
                                 onfail="ONOS service did not start properly" )

        main.step( "Starting Mininet Topology" )
        topoResult = main.Mininet1.startNet( topoFile=topology )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

        main.step( "Start ONOS cli" )
        cliResult =  main.ONOScli1.startOnosCli( ONOSIp=main.ONOS1ip )
        stepResult = cliResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )

    def CASE11( self, main ):
        """
        Assign mastership to controllers
        """
        import re
        main.log.report( "Assigning switches to controllers" )
        main.log.case( "Assigning swithes to controllers" )

        main.step( "Assigning switches to controllers" )
        assignResult = main.TRUE
        for i in range( 1, ( main.numSwitch + 1 ) ):
            main.Mininet1.assignSwController( sw=str( i ),
                                              count=1,
                                              ip1=main.ONOS1ip,
                                              port1=main.ONOS1port )
        for i in range( 1, ( main.numSwitch + 1 ) ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + main.ONOS1ip, response ):
                assignResult = assignResult and main.TRUE
            else:
                assignResult = main.FALSE
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switches" +
                                        "to controller",
                                 onfail="Failed to assign switches to " +
                                        "controller" )


    def CASE1000( self, main ):
        """
            Add host intents between 2 host
        """
        import time
        import json
        
        item = []
        
        ipv4 = { 'name':'', 'host1':, 'host2': }

        main.case( "Add host intents between 2 host" )

        main.step(" Discover host using arping" )
        


        main.step( "Discover host using arping" )
        step1Result = main.TRUE
        main.hostMACs = []
        main.hostId = []
        #Listing host MAC addresses
        for i in range( 1 , 7 ):
            main.hostMACs.append( "00:00:00:00:00:" +
                                str( hex( i )[ 2: ] ).zfill( 2 ).upper() )
        for macs in main.hostMACs:
            main.hostId.append( macs + "/-1" )
        host1 = main.hostId[ 0 ]
        host2 = main.hostId[ 1 ]
        # Use arping to discover the hosts
        main.LincOE2.arping( host = "h1" )
        main.LincOE2.arping( host = "h2" )
        time.sleep( 5 )
        hostsDict = main.ONOS3.hosts()
        if not len( hostsDict ):
            step1Result = main.FALSE
        # Adding host intent
        utilities.assert_equals(
            expect=main.TRUE,
            actual=step1Result,
            onpass="Hosts discovered",
            onfail="Failed to discover hosts")

        main.step( "Adding host intents to h1 and h2" )
        step2Result = main.TRUE
        intentsId = []
        intent1 = main.ONOS3.addHostIntent( hostIdOne = host1,
                                            hostIdTwo = host2 )
        intentsId.append( intent1 )
        time.sleep( 5 )
        intent2 = main.ONOS3.addHostIntent( hostIdOne = host2,
                                            hostIdTwo = host1 )
        intentsId.append( intent2 )
        # Checking intents state before pinging
        main.log.info( "Checking intents state" )
        time.sleep( 15 )
        intentResult = main.ONOS3.checkIntentState( intentsId = intentsId )
        #check intent state again if intents are not in installed state
        if not intentResult:
           intentResult = main.ONOS3.checkIntentState( intentsId = intentsId )
        step2Result = intentResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=step2Result,
                                 onpass="All intents are in INSTALLED state ",
                                 onfail="Some of the intents are not in " +
                                        "INSTALLED state " )

        # pinging h1 to h2 and then ping h2 to h1
        main.step( "Pinging h1 and h2" )
        step3Result = main.TRUE
        pingResult = main.TRUE
        pingResult = main.LincOE2.pingHostOptical( src="h1", target="h2" )
        pingResult = pingResult and main.LincOE2.pingHostOptical( src="h2",
                                                                  target="h1" )
        step3Result = pingResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=step3Result,
                                 onpass="Pinged successfully between h1 and h2",
                                 onfail="Pinged failed between h1 and h2" )
        # Removed all added host intents
        main.step( "Removing host intents" )
        step4Result = main.TRUE
        removeResult = main.TRUE
        # Check remaining intents
        intentsJson = json.loads( main.ONOS3.intents() )
        main.ONOS3.removeIntent( intentId=intent1, purge=True )
        main.ONOS3.removeIntent( intentId=intent2, purge=True )
        for intents in intentsJson:
            main.ONOS3.removeIntent( intentId=intents.get( 'id' ),
                                     app='org.onosproject.optical',
                                     purge=True )
        print json.loads( main.ONOS3.intents() )
        if len( json.loads( main.ONOS3.intents() ) ):
            removeResult = main.FALSE
        step4Result = removeResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=step4Result,
                                 onpass="Successfully removed host intents",
                                 onfail="Failed to remove host intents" )
        case25Result = step1Result and step2Result and step3Result and \
                       step4Result
        utilities.assert_equals( expect=main.TRUE,
                                 actual=case25Result,
                                 onpass="Add host intent successful",
                                 onfail="Add host intent failed" )
