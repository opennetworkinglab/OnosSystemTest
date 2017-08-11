"""
Copyright 2015 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""

# ScaleOutTemplate -> flowTP
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os.path


class SCPFflowTp1g:

    def __init__( self ):
        self.default = ''

    def CASE0( self, main ):
        import time
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error("ONOSSetup not found. exiting the test")
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        try:
            #Load values from params file
            cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            BENCHUser = main.params[ 'BENCH' ][ 'user' ]
            BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
            main.scale = ( main.params[ 'SCALE' ]  ).split( "," )
            main.flowRuleCfg = main.params[ 'CFG' ][ 'flowRule' ]
            main.neighbor = ( main.params[ 'TEST' ][ 'neighbors' ] ).split( "," )
            main.nullProviderCfg = main.params[ 'CFG' ][ 'nullProvider' ]
            isFlowObj = main.params[ 'TEST' ][ 'flowObj' ]
            if isFlowObj == 'true':
               resultFile = main.params[ 'TEST' ][ 'flowObjResultFile' ]
            else:
               resultFile = main.params[ 'TEST' ][ 'flowResultFile' ]
            stepResult = main.testSetUp.envSetup()
            resultsDB = open( str( resultFile ), "w+" )
            resultsDB.close()
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )
        main.commit = ( main.commit.split( " " ) )[ 1 ]

    def CASE1( self, main ):
        main.testSetUp.ONOSSetUp( "localhost", main.Cluster, True, cellName=cellName )
        main.log.info( "Startup sequence complete" )
        main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress, [ "ERROR", "WARNING", "EXCEPT" ], outputMode="d" )

    def CASE2( self, main ):
        #
        # This is the flow/flowObjective TP test
        #
        import os.path
        import numpy
        import math
        import time
        import datetime
        import traceback

        testCMD = [ 0, 0, 0, 0 ]
        warmUp = int( main.params[ 'TEST' ][ 'warmUp' ] )
        sampleSize = int( main.params[ 'TEST' ][ 'sampleSize' ] )
        switches = int( main.params[ 'TEST' ][ 'switches' ] )
        testCMD[ 0 ] = main.params[ 'TEST' ][ 'testCMD0' ]
        testCMD[ 1 ] = main.params[ 'TEST' ][ 'testCMD1' ]
        testCMD[ 2 ] = main.params[ 'TEST' ][ 'testCMD2' ]
        testCMD[ 3 ] = main.params[ 'TEST' ][ 'testCMD3' ]
        flowObjType = main.params[ 'TEST' ][ 'flowObjType' ]
        isFlowObj = main.params[ 'TEST' ][ 'flowObj' ]
        cooldown = main.params[ 'TEST' ][ 'cooldown' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        homeDir = os.path.expanduser( '~' )
        flowRuleBackup = str( main.params[ 'TEST' ][ 'enableFlowRuleStoreBackup' ] )
        main.log.info( "Flow Rule Backup is set to:" + flowRuleBackup )

        servers = str( main.Cluster.numCtrls )
        neighbors = '0' if main.neighbor.pop( 0 ) == '0' else str( main.Cluster.numCtrls - 1 )
        main.log.info( "Number of Neighbors: " + neighbors )
        ts = time.time()
        st = datetime.datetime.fromtimestamp( ts ).strftime( '%Y-%m-%d %H:%M:%S' )
        main.step( "\tSTARTING TEST" )
        main.step( "\tLOADING FROM SERVERS:  \t" + str( main.Cluster.numCtrls ) )
        main.step( "\tNEIGHBORS:\t" + neighbors )
        main.log.info( "=============================================================" )
        main.log.info( "=============================================================" )
        #write file to configure nil link
        ipCSV = ""
        for i in range ( main.Cluster.maxCtrls ):
            tempstr = "ip" + str( i + 1 )
            ipCSV += main.params[ 'CTRL' ][ tempstr ]
            if i + 1 < main.Cluster.maxCtrls:
                ipCSV +=","

        main.ONOSbench.onosCfgSet( main.Cluster.active( 0 ).ipAddress,
                                   main.flowRuleCfg,
                                   "backupCount 1" )
        for i in range( 3 ):
            main.ONOSbench.onosCfgSet( main.Cluster.active( 0 ).ipAddress,
                                       main.nullProviderCfg,
                                       "deviceCount 35" )
            main.ONOSbench.onosCfgSet( main.Cluster.active( 0 ).ipAddress,
                                       main.nullProviderCfg,
                                       "topoShape linear" )
            main.ONOSbench.onosCfgSet( main.Cluster.active( 0 ).ipAddress,
                                       main.nullProviderCfg,
                                       "enabled true" )

            time.sleep( 5 )
            main.ONOSbench.handle.sendline( "onos $OC1 summary" )
            main.ONOSbench.handle.expect( ":~" )
            check = main.ONOSbench.handle.before
            main.log.info( "\nStart up check: \n" + check + "\n" )
            if "SCC(s)=1," in check:
                main.ONOSbench.handle.sendline( "onos $OC1 balance-masters" )
                main.ONOSbench.handle.expect( ":~" )
                time.sleep( 5 )
                main.ONOSbench.handle.sendline( "onos $OC1 roles " )
                main.ONOSbench.handle.expect ( ":~" )
                main.log.info( "switch masterships:" + str( main.ONOSbench.handle.before ) )
                break
            time.sleep( 5 )

        #divide flows/flowObjectives
        if isFlowObj == 'true':
           toInstall = "FlowObjectives"
           installCount = int( main.params[ 'TEST' ][ 'flowObjectives' ] )
           ifFailed = "FLOW_OBJ_TESTER.PY FAILURE"
           resultFile = main.params[ 'TEST' ][ 'flowObjResultFile' ]
        else:
           toInstall = "Flows"
           installCount = int( main.params[ 'TEST' ][ 'flows' ] )
           ifFailed = "FLOW_TESTER.PY FAILURE"
           resultFile = main.params[ 'TEST' ][ 'flowResultFile' ]
        main.log.info( toInstall + " Target  = " + str( installCount ) )

        installCountPerSwitch = ( installCount *max( int ( neighbors ) + 1, int( servers ) ) )/( ( int( neighbors ) + 1 )*int( servers )*( switches ) )

        main.log.info( toInstall + " per switch = " + str( installCountPerSwitch ) )
        #build list of servers in "$OC1, $OC2...." format
        serverEnvVars = ""
        for i in range( int( servers ) ):
            serverEnvVars += ( "-s " + main.Cluster.active( i ).ipAddress + " " )

        data = [ [ "" ]*int( servers ) ]*int( sampleSize )
        maxes = [ "" ]*int( sampleSize )

        flowCMD = "python3 " + homeDir + "/onos/tools/test/bin/"
        if isFlowObj == 'true':
           flowCMD += testCMD[ 2 ] + " " + str( installCountPerSwitch ) + " " + testCMD[ 1 ]
           flowCMD += " " + neighbors + " " + testCMD[ 3 ] + " " + str( flowObjType ) + " " + str( serverEnvVars ) + "-j"
        else:
           flowCMD += testCMD[ 0 ] + " " + str( installCountPerSwitch ) + " " + testCMD[ 1 ]
           flowCMD += " " + neighbors + " " + str( serverEnvVars ) + "-j"

        main.log.info( flowCMD )
        #time.sleep( 60 )

        for test in range( 0, warmUp + sampleSize ):
            if test < warmUp:
                main.log.info( "Warm up " + str( test + 1 ) + " of " + str( warmUp ) )
            else:
                 main.log.info( "====== Test run: " + str( test-warmUp+1 ) + " ======" )

            main.ONOSbench.handle.sendline( flowCMD )
            main.ONOSbench.handle.expect( ":~" )
            rawResult = main.ONOSbench.handle.before
            main.log.info( "Raw results: \n" + rawResult + "\n" )

            if "failed" in rawResult:
                main.log.report( ifFailed )
                main.log.report( " \n" + rawResult + " \n" )
                for ctrl in main.Cluster.active():
                    main.log.report( "=======================================================" )
                    main.log.report( ctrl.name + "LOG REPORT" )
                    main.ONOSbench.logReport( ctrl.ipAddress, [ "ERROR", "WARNING", "EXCEPT" ], outputMode="d" )
                main.ONOSbench.handle.sendline( "onos $OC1 flows" )
                main.ONOSbench.handle.expect( ":~" )
                main.log.info( main.ONOSbench.handle.before )

                break
            result = [ "" ]*( main.Cluster.numCtrls )

            rawResult = rawResult.splitlines()

            for node in range( main.Cluster.numCtrls ):
                for line in rawResult:
                    #print( "line: " + line )
                    if main.Cluster.active( node ).ipAddress in line and "server" in line:
                        temp = line.split( " " )
                        for word in temp:
                            #print ( "word: " + word )
                            if "elapsed" in repr( word ):
                                index = temp.index( word ) + 1
                                myParsed = ( temp[ index ] ).replace( ",", "" )
                                myParsed = myParsed.replace( "}", "" )
                                myParsed = int( myParsed )
                                result[ node ] = myParsed
                                main.log.info( main.Cluster.active( node ).ipAddress + " : " + str( myParsed ) )
                                break

            if test >= warmUp:
                for i in result:
                    if i == "":
                        main.log.error( "Missing data point, critical failure incoming" )

                print result
                maxes[ test-warmUp ] = max( result )
                main.log.info( "Data collection iteration: " + str( test-warmUp ) + " of " + str( sampleSize ) )
                main.log.info( "Throughput time: " + str( maxes[ test-warmUp ] ) + "(ms)" )

                data[ test-warmUp ] = result

            # wait for flows = 0
            for checkCount in range( 0, 5 ):
                time.sleep( 10 )
                main.ONOSbench.handle.sendline( "onos $OC1 summary" )
                main.ONOSbench.handle.expect( ":~" )
                flowCheck = main.ONOSbench.handle.before
                if "flows=0," in flowCheck:
                    main.log.info( toInstall + " removed" )
                    break
                else:
                    for line in flowCheck.splitlines():
                        if "flows=" in line:
                            main.log.info( "Current Summary: " + line )
                if checkCount == 2:
                    main.log.info( toInstall + " are stuck, moving on " )
            time.sleep( 5 )

        main.log.info( "raw data: " + str( data ) )
        main.log.info( "maxes:" + str( maxes ) )


        # report data
        print( "" )
        main.log.info( "\t Results (measurments are in milliseconds)" )
        print( "" )

        nodeString = ""
        for i in range( 1, int( servers ) + 1 ):
            nodeString += ( "\tNode " + str( i ) )

        for test in range( 0, sampleSize ):
            main.log.info( "\t Test iteration " + str( test + 1 ) )
            main.log.info( "\t------------------" )
            main.log.info( nodeString )
            resultString = ""

            for i in range( 0, int( servers ) ):
                resultString += ( "\t" + str( data[ test ][ i ] ) )
            main.log.info( resultString )
            print( "\n" )

        avgOfMaxes = numpy.mean( maxes )
        main.log.info( "Average of max value from each test iteration: " + str( avgOfMaxes ) )

        stdOfMaxes = numpy.std( maxes )
        main.log.info( "Standard Deviation of max values: " + str( stdOfMaxes ) )
        print( "\n\n" )

        avgTP = int( installCount )  / avgOfMaxes #result in kflows/second

        tp = []
        for i in maxes:
            tp.append( ( int( installCount ) / i ) )

        stdTP = numpy.std( tp )

        main.log.info( "Average thoughput:  " + str( avgTP ) + " K" + toInstall + "/second" )
        main.log.info( "Standard deviation of throughput: " + str( stdTP ) + " K" + toInstall + "/second" )

        resultsLog = open( str( resultFile ), "a" )
        resultString = ( "'" + main.commit + "'," )
        resultString += ( "'1gig'," )
        resultString += ( str( installCount ) + "," )
        resultString += ( str( main.Cluster.numCtrls ) + "," )
        resultString += ( neighbors + "," )
        resultString += ( str( avgTP ) + "," + str( stdTP ) + "\n" )
        resultsLog.write( resultString )
        resultsLog.close()

        main.log.report( "Result line to file: " + resultString )

        main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress, [ "ERROR", "WARNING", "EXCEPT" ], outputMode="d" )