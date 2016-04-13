# ScaleOutTemplate --> CbenchBM
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os
import os.path


class SCPFcbench:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):

        import time
        import os
        global init
        main.case("pre-condition for cbench test.")

        try:
            if type(init) is not bool:
                init = False
        except NameError:
            init = False

        #Load values from params file
        checkoutBranch = main.params[ 'GIT' ][ 'checkout' ]
        gitPull = main.params[ 'GIT' ][ 'autopull' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        CBENCHuser = main.params[ 'CBENCH'][ 'user' ]
        MN1Ip = os.environ[ main.params[ 'MN' ][ 'ip1' ] ]
        maxNodes = int(main.params[ 'availableNodes' ])
        skipMvn = main.params[ 'TEST' ][ 'skipCleanInstall' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        cellApps = main.params[ 'ENV' ][ 'cellApps' ]

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        if init == False:
            init = True
            global clusterCount             #number of nodes running
            global ONOSIp                   #list of ONOS IP addresses
            global scale

            clusterCount = 0
            ONOSIp = [ 0 ]
            scale = (main.params[ 'SCALE' ]).split(",")
            clusterCount = int(scale[0])

            #Populate ONOSIp with ips from params
            for i in range(1, maxNodes + 1):
                ipString = os.environ[main.params['CTRL']['ip1']]
                ONOSIp.append(ipString)

            #mvn clean install, for debugging set param 'skipCleanInstall' to yes to speed up test
            if skipMvn != "yes":
                mvnResult = main.ONOSbench.cleanInstall()

            #git
            main.step( "Git checkout and pull " + checkoutBranch )
            if gitPull == 'on':
                checkoutResult = main.ONOSbench.gitCheckout( checkoutBranch )
                pullResult = main.ONOSbench.gitPull()

            else:
                checkoutResult = main.TRUE
                pullResult = main.TRUE
                main.log.info( "Skipped git checkout and pull" )

        # -- END OF INIT SECTION --#

        clusterCount = int(scale[0])
        scale.remove(scale[0])

        #kill off all onos processes
        main.log.step("Safety check, killing all ONOS processes")
        main.log.step("before initiating environment setup")
        for node in range(1, maxNodes + 1):
            main.ONOSbench.onosDie(ONOSIp[node])

        #Uninstall everywhere
        main.log.step( "Cleaning Enviornment..." )
        for i in range(1, maxNodes + 1):
            main.log.info(" Uninstalling ONOS " + str(i) )
            main.ONOSbench.onosUninstall( ONOSIp[i] )

        time.sleep(10)
        main.ONOSbench.handle.sendline(" ")
        main.ONOSbench.handle.expect(":~")
        print "pexpect: \n" + main.ONOSbench.handle.before


        print "Cellname is: "+ cellName + "ONOS IP is: " + str(ONOSIp)
        main.ONOSbench.createCellFile(BENCHIp,cellName,MN1Ip,cellApps,[ONOSIp[1]])

        main.step( "Set Cell" )
        main.ONOSbench.setCell(cellName)

        #main.ONOSbench.handle.sendline(" ")
        #main.ONOSbench.handle.expect(":~")
        #print "pexpect: \n" + main.ONOSbench.handle.before

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

        main.step( "verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()

        main.log.report( "Initializing " + str( clusterCount ) + " node cluster." )
        for node in range(1, clusterCount + 1):
            main.log.info("Starting ONOS " + str(node) + " at IP: " + ONOSIp[node])
            main.ONOSbench.onosInstall( ONOSIp[node])

        for node in range(1, clusterCount + 1):
            for i in range( 2 ):
                isup = main.ONOSbench.isup( ONOSIp[node] )
                if isup:
                    main.log.info("ONOS " + str(node) + " is up\n")
                    break
            if not isup:
                main.log.report( "ONOS " + str(node) + " didn't start!" )
        main.log.info("Startup sequence complete")

        for i in range(5):
            main.ONOSbench.onosCfgSet(ONOSIp[1], "org.onosproject.fwd.ReactiveForwarding","packetOutOnly true")
            time.sleep(5)
            main.ONOSbench.handle.sendline("onos $OC1 cfg get|grep packetOutOnly")
            main.ONOSbench.handle.expect(":~")
            check = main.ONOSbench.handle.before
            if "value=true" in check:
                main.log.info("cfg set successful")
                stepResult = main.TRUE
                break
            if i == 4:
                main.log.info("Cfg set failed")
                stepResult = main.FALSE
            else:
                time.sleep(5)

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully configure onos for cbench test ",
                                 onfail="Failed to configure onos for cbench test" )




    def CASE2( self, main ):
        main.case("Running Cbench")
        main.step("Issuing cbench commands and grab returned results")
        validFlag = False
        cbenchCMD = main.params[ 'TEST' ][ 'cbenchCMD' ]
        mode = main.params[ 'TEST' ][ 'mode' ]
        if mode != "t":
            mode = " "

        runCbench = ( "ssh " + CBENCHuser + "@" + ONOSIp[1] + " " + cbenchCMD + mode )
        main.ONOSbench.handle.sendline(runCbench)
        time.sleep(30)
        main.ONOSbench.handle.expect(":~")
        output = main.ONOSbench.handle.before
        main.log.info(output)

        output = output.splitlines()
        for line in output:
            if "RESULT: " in line:
                validFlag = True
                print line
                resultLine = line.split(" ")
                for word in resultLine:
                    if word == "min/max/avg/stdev":
                        resultsIndex = resultLine.index(word)
                        print resultsIndex
                        break

                finalDataString = resultLine[resultsIndex + 2]
                print finalDataString
                finalDataList = finalDataString.split("/")
                avg = finalDataList[2]
                stdev = finalDataList[3]

                main.log.info("Average: \t\t\t" + avg)
                main.log.info("Standard Deviation: \t" + stdev)


                commit = main.ONOSbench.getVersion()
                commit = (commit.split(" "))[1]

                try:
                    dbFileName="/tmp/CbenchDB"
                    dbfile = open(dbFileName, "w+")
                    temp = "'" + commit + "',"
                    temp += "'" + mode + "',"
                    temp += "'" + avg + "',"
                    temp += "'" + stdev + "'\n"
                    dbfile.write(temp)
                    dbfile.close()
                    main.ONOSbench.logReport(ONOSIp[1], ["ERROR", "WARNING", "EXCEPT"], outputMode="d")
                except IOError:
                    main.log.warn("Error opening " + dbFileName + " to write results.")

                stepResult = main.TRUE
                break
        if ( validFlag == False ):
            main.log.warn("Cbench Test produced no valid results!!!!")
            stepResult = main.FALSE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully tested onos for cbench. ",
                                 onfail="Failed to obtain valid onos cbench result!" )






