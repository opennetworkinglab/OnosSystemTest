# ScaleOutTemplate
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os.path


class IntentInstallWithdrawLat:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):           
                                        
        import time                     
        global init       
        try: 
            if type(init) is not bool: 
                init = False  
        except NameError: 
            init = False 
       
        #Load values from params file
        checkoutBranch = main.params[ 'GIT' ][ 'checkout' ]
        gitPull = main.params[ 'GIT' ][ 'autopull' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        Apps = main.params[ 'ENV' ][ 'cellApps' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        maxNodes = int(main.params[ 'availableNodes' ])
        skipMvn = main.params[ 'TEST' ][ 'skipCleanInstall' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]        
        switchCount = main.params[ 'TEST' ][ 'switchCount' ]

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
                ipString = 'ip' + str(i) 
                ONOSIp.append(main.params[ 'CTRL' ][ ipString ])   
            
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
        main.log.step("before initiating enviornment setup")
        for node in range(1, maxNodes + 1):
            main.ONOSbench.onosDie(ONOSIp[node])
        
        #Uninstall everywhere
        main.log.step( "Cleaning Enviornment..." )
        for i in range(1, maxNodes + 1):
            main.log.info(" Uninstalling ONOS " + str(i) )
            main.ONOSbench.onosUninstall( ONOSIp[i] )
       
        #construct the cell file
        main.log.info("Creating cell file")
        cellIp = []
        for node in range (1, clusterCount + 1):
            cellIp.append(ONOSIp[node])

        main.ONOSbench.createCellFile(BENCHIp,cellName,MN1Ip,str(Apps), *cellIp)

        main.step( "Set Cell" )
        main.ONOSbench.setCell(cellName)
        
        main.ONOSbench.createLinkGraphFile(BENCHIp, cellIp, switchCount)        

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()  

        main.step( "verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()
      
        main.log.report( "Initializeing " + str( clusterCount ) + " node cluster." )
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

        main.ONOS1cli.startOnosCli( ONOSIp[1] )
        main.log.info("Startup sequence complete")

        main.ONOSbench.configNullDev(cellIp, switchCount) 

    def CASE2( self, main ):
         
        import time
        import numpy

        sampleSize = int(main.params[ 'TEST' ][ 'sampleSize' ])
        warmUp = int(main.params[ 'TEST' ][ 'warmUp' ])
        intentsList = (main.params[ 'TEST' ][ 'intents' ]).split(",")
        switchCount = int(main.params[ 'TEST' ][ 'switchCount' ])
        debug = main.params[ 'TEST' ][ 'switchCount' ]
        for i in range(0,len(intentsList)):
            intentsList[i] = int(intentsList[i])

        if debug == "True":
            debug = True
        else:
            debug = False

        linkCount = 0
        for i in range(0,10):
            main.ONOSbench.handle.sendline("onos $OC1 links|wc -l")
            main.ONOSbench.handle.expect(":~")
            linkCount = main.ONOSbench.handle.before
            if debug: main.log.info("Link Count check: " + linkCount)
            if str((switchCount*2)-2) in linkCount:
                break
            time.sleep(2)

        links = "--"
        while "=null:" not in links:
            if debug: main.log.info("top of loop")
            main.ONOSbench.handle.sendline("onos $OC1 links")
            main.ONOSbench.handle.expect(":~")
            links = main.ONOSbench.handle.before
            if debug: main.log.info(str(links))
            time.sleep(1)
        links = links.splitlines()
        templinks = links

        tempDevices = []
        for line in links:
            temp = line.split(" ")
            temp[0].replace("src=","")
            temp[0] = (temp[0].split("/"))[0]
            tempDevices.append(temp[0])

        tempDevices.sort()
        devices = []
        for i in tempDevices:
            if "src=null" in i:
                devices.append(i.replace("src=", ""))
        if debug: main.log.info(str(devices))

        ingress = devices[0]
        egress = devices.pop()
        if debug: main.log.info(ingress)
        if debug: main.log.info(egress)

        for intentSize in intentsList:
            cmd = "onos $OC1 push-test-intents "
            cmd += ingress + "/6 "
            cmd += egress + "/5 "
            cmd += str(intentSize) + " 1"
            installed = []
            withdrawn = []

            for run in range(0, (warmUp + sampleSize)):
                if run > warmUp:
                    time.sleep(5)

                myRawResult = "--"
                while "ms" not in myRawResult:
                    main.ONOSbench.handle.sendline(cmd)
                    main.ONOSbench.handle.expect(":~")
                    myRawResult = main.ONOSbench.handle.before
                    if debug: main.log.info(myRawResult)

                if debug: main.log.info(myRawResult)

                if run >= warmUp:
                    myRawResult = myRawResult.splitlines()
                    for line in myRawResult:
                        if "install" in line:
                            installed.append(int(line.split(" ")[5]))

                    for line in myRawResult:
                        if "withdraw" in line:
                            withdrawn.append(int(line.split(" ")[5]))

                    print("installed: " + str(installed))
                    print("withraw: " + str(withdrawn) + "\n")

            main.log.report("----------------------------------------------------")
            main.log.report("Scale: " + str(clusterCount) + "\tIntent batch size: " + str(intentSize))
            main.log.report("Data samples: " + str(sampleSize) + "\tWarm up tests: " + str(warmUp))
            main.log.report("Installed average: " + str(numpy.mean(installed)))
            main.log.report("Installed standard deviation: " + str(numpy.std(installed)))
            main.log.report("Withdraw average: " + str(numpy.mean(withdrawn)))
            main.log.report("Withdraw standard deviation: " + str(numpy.std(withdrawn)))
            main.log.report("     ")

