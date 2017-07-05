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

    def CASE1( self, main ):

        import time
        global init
        try:
            if type( init ) is not bool:
                init = False
        except NameError:
            init = False

        main.log.info( "==========DEBUG VERSION 3===========" )

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        if init == False:
            try:
                init = True
                try:
                    from tests.dependencies.ONOSSetup import ONOSSetup
                    main.testSetUp = ONOSSetup()
                except ImportError:
                    main.log.error( "ONOSSetup not found. exiting the test" )
                    main.exit()
                main.testSetUp.envSetupDescription()
                #Load values from params file
                cellName = main.params[ 'ENV' ][ 'cellName' ]
                main.apps = main.params[ 'ENV' ][ 'cellApps' ]
                BENCHUser = main.params[ 'BENCH' ][ 'user' ]
                BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
                main.scale = ( main.params[ 'SCALE' ]  ).split( "," )
                stepResult = main.testSetUp.envSetup()
                resultsDB = open( "/tmp/flowTP1gDB", "w+" )
                resultsDB.close()
            except Exception as e:
                main.testSetUp.envSetupException( e )
            main.testSetUp.evnSetupConclusion( stepResult )
            main.commit = (main.commit.split(" "))[1]
        # -- END OF INIT SECTION --#

        main.testSetUp.ONOSSetUp( "localhost", True, cellName=cellName )

        main.log.info("Startup sequence complete")
        main.ONOSbench.logReport(main.ONOSip[0], ["ERROR", "WARNING", "EXCEPT"], outputMode="d")

    def CASE2( self, main ):
        #
        # This is the flow TP test
        #
        import os.path
        import numpy
        import math
        import time
        import datetime
        import traceback

        global currentNeighbors
        try:
            currentNeighbors
        except:
            currentNeighbors = (main.params[ 'TEST' ][ 'neighbors' ]).split(",")[0]
        else:
            if currentNeighbors == "r":      #reset
                currentNeighbors = "0"
            else:
                currentNeighbors = "a"

        testCMD = [ 0,0,0,0 ]
        warmUp = int(main.params[ 'TEST' ][ 'warmUp' ])
        sampleSize = int(main.params[ 'TEST' ][ 'sampleSize' ])
        switches = int(main.params[ 'TEST' ][ 'switches' ])
        neighborList = (main.params[ 'TEST' ][ 'neighbors' ]).split(",")
        testCMD[0] = main.params[ 'TEST' ][ 'testCMD0' ]
        testCMD[1] = main.params[ 'TEST' ][ 'testCMD1' ]
        cooldown = main.params[ 'TEST' ][ 'cooldown' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        homeDir = os.path.expanduser('~')
        flowRuleBackup = str(main.params[ 'TEST' ][ 'enableFlowRuleStoreBackup' ])
        main.log.info("Flow Rule Backup is set to:" + flowRuleBackup)

        servers = str( main.numCtrls )

        if main.numCtrls == 1:
            neighborList = ['0']
            currentNeighbors = "r"
        else:
            if currentNeighbors == "a":
                neighborList = [ str( main.numCtrls - 1 ) ]
                currentNeighbors = "r"
            else:
                neighborList = ['0']

        main.log.info("neightborlist: " + str(neighborList))

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        for n in neighborList:
            main.step("\tSTARTING TEST")
            main.step("\tLOADING FROM SERVERS:  \t" + str( main.numCtrls ) )
            main.step("\tNEIGHBORS:\t" + n )
            main.log.info("=============================================================")
            main.log.info("=============================================================")
            #write file to configure nil link
            ipCSV = ""
            for i in range ( main.maxNodes ):
                tempstr = "ip" + str( i + 1 )
                ipCSV += main.params[ 'CTRL' ][ tempstr ]
                if i + 1 < main.maxNodes:
                    ipCSV +=","

            main.ONOSbench.onosCfgSet(main.ONOSip[0], "org.onosproject.store.flow.impl.DistributedFlowRuleStore", "backupCount 1")
            for i in range(3):
                main.ONOSbench.onosCfgSet(main.ONOSip[0], "org.onosproject.provider.nil.NullProviders", "deviceCount 35")
                main.ONOSbench.onosCfgSet(main.ONOSip[0], "org.onosproject.provider.nil.NullProviders", "topoShape linear")
                main.ONOSbench.onosCfgSet(main.ONOSip[0], "org.onosproject.provider.nil.NullProviders", "enabled true")

                time.sleep(5)
                main.ONOSbench.handle.sendline("onos $OC1 summary")
                main.ONOSbench.handle.expect(":~")
                check = main.ONOSbench.handle.before
                main.log.info("\nStart up check: \n" + check + "\n")
                if "SCC(s)=1," in check:
                    main.ONOSbench.handle.sendline( "onos $OC1 balance-masters" )
                    main.ONOSbench.handle.expect( ":~" )
                    time.sleep(5)
                    main.ONOSbench.handle.sendline( "onos $OC1 roles ")
                    main.ONOSbench.handle.expect ( ":~" )
                    main.log.info( "switch masterships:" + str( main.ONOSbench.handle.before ) )
                    break
                time.sleep(5)

            #devide flows
            flows = int(main.params[ 'TEST' ][ 'flows' ])
            main.log.info("Flow Target  = " + str(flows))

            flows = (flows *max(int(n)+1,int(servers)))/((int(n) + 1)*int(servers)*(switches))

            main.log.info("Flows per switch = " + str(flows))

            #build list of servers in "$OC1, $OC2...." format
            serverEnvVars = ""
            for i in range( int( servers ) ):
                serverEnvVars += ( "-s " + main.ONOSip[ i ] + " " )

            data = [[""]*int(servers)]*int(sampleSize)
            maxes = [""]*int(sampleSize)

            flowCMD = "python3 " + homeDir + "/onos/tools/test/bin/"
            flowCMD += testCMD[0] + " " + str(flows) + " " + testCMD[1]
            flowCMD += " " + str(n) + " " + str(serverEnvVars) + "-j"

            main.log.info(flowCMD)
            #time.sleep(60)

            for test in range(0, warmUp + sampleSize):
                if test < warmUp:
                    main.log.info("Warm up " + str(test + 1) + " of " + str(warmUp))
                else:
                     main.log.info("====== Test run: " + str(test-warmUp+1) + " ======")

                main.ONOSbench.handle.sendline(flowCMD)
                main.ONOSbench.handle.expect(":~")
                rawResult = main.ONOSbench.handle.before
                main.log.info("Raw results: \n" + rawResult + "\n")

                if "failed" in rawResult:
                    main.log.report("FLOW_TESTER.PY FAILURE")
                    main.log.report( " \n" + rawResult + " \n")
                    for i in range( main.numCtrls ):
                        main.log.report("=======================================================")
                        main.log.report(" ONOS " + str( i + 1 ) + "LOG REPORT")
                        main.ONOSbench.logReport( main.ONOSip[ i ], ["ERROR", "WARNING", "EXCEPT"], outputMode="d" )
                    main.ONOSbench.handle.sendline("onos $OC1 flows")
                    main.ONOSbench.handle.expect(":~")
                    main.log.info(main.ONOSbench.handle.before)

                    break

            ########################################################################################
                result = [""]*( main.numCtrls )

                #print("rawResult: " + rawResult)

                rawResult = rawResult.splitlines()

                for node in range( main.numCtrls ):
                    for line in rawResult:
                        #print("line: " + line)
                        if main.ONOSip[ node ] in line and "server" in line:
                            temp = line.split( " " )
                            for word in temp:
                                #print ("word: " + word)
                                if "elapsed" in repr(word):
                                    index = temp.index(word) + 1
                                    myParsed = (temp[index]).replace(",","")
                                    myParsed = myParsed.replace("}","")
                                    myParsed = int(myParsed)
                                    result[ node ] = myParsed
                                    main.log.info( main.ONOSip[ node ] + " : " + str( myParsed ) )
                                    break

                if test >= warmUp:
                    for i in result:
                        if i == "":
                            main.log.error("Missing data point, critical failure incoming")

                    print result
                    maxes[test-warmUp] = max(result)
                    main.log.info("Data collection iteration: " + str(test-warmUp) + " of " + str(sampleSize))
                    main.log.info("Throughput time: " + str(maxes[test-warmUp]) + "(ms)")

                    data[test-warmUp] = result

                # wait for flows = 0
                for checkCount in range(0,5):
                    time.sleep(10)
                    main.ONOSbench.handle.sendline("onos $OC1 summary")
                    main.ONOSbench.handle.expect(":~")
                    flowCheck = main.ONOSbench.handle.before
                    if "flows=0," in flowCheck:
                        main.log.info("Flows removed")
                        break
                    else:
                        for line in flowCheck.splitlines():
                            if "flows=" in line:
                                main.log.info("Current Summary: " + line)
                    if checkCount == 2:
                        main.log.info("Flows are stuck, moving on ")


                time.sleep(5)

            main.log.info("raw data: " + str(data))
            main.log.info("maxes:" + str(maxes))


            # report data
            print("")
            main.log.info("\t Results (measurments are in milliseconds)")
            print("")

            nodeString = ""
            for i in range(1, int(servers) + 1):
                nodeString += ("\tNode " + str(i))

            for test in range(0, sampleSize ):
                main.log.info("\t Test iteration " + str(test + 1) )
                main.log.info("\t------------------")
                main.log.info(nodeString)
                resultString = ""

                for i in range(0, int(servers) ):
                    resultString += ("\t" + str(data[test][i]) )
                main.log.info(resultString)

                print("\n")

            avgOfMaxes = numpy.mean(maxes)
            main.log.info("Average of max value from each test iteration: " + str(avgOfMaxes))

            stdOfMaxes = numpy.std(maxes)
            main.log.info("Standard Deviation of max values: " + str(stdOfMaxes))
            print("\n\n")

            avgTP = int(main.params[ 'TEST' ][ 'flows' ])  / avgOfMaxes #result in kflows/second

            tp = []
            for i in maxes:
                tp.append((int(main.params[ 'TEST' ][ 'flows' ]) / i ))

            stdTP = numpy.std(tp)

            main.log.info("Average thoughput:  " + str(avgTP) + " Kflows/second" )
            main.log.info("Standard deviation of throughput: " + str(stdTP) + " Kflows/second")

            resultsLog = open( "/tmp/flowTP1gDB", "a" )
            resultString = ( "'" + main.commit + "'," )
            resultString += ( "'1gig'," )
            resultString += ( (main.params[ 'TEST' ][ 'flows' ] ) + "," )
            resultString += ( str( main.numCtrls ) + "," )
            resultString += ( str( n ) + "," )
            resultString += ( str( avgTP ) + "," + str( stdTP ) + "\n" )
            resultsLog.write( resultString )
            resultsLog.close()

            main.log.report( "Result line to file: " + resultString )

        main.ONOSbench.logReport( main.ONOSip[ 0 ], [ "ERROR", "WARNING", "EXCEPT" ], outputMode="d" )
