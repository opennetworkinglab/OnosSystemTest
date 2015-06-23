# ScaleOutTemplate --> CbenchBM
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os.path


class CbenchBM:

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
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        maxNodes = int(main.params[ 'availableNodes' ])
        skipMvn = main.params[ 'TEST' ][ 'skipCleanInstall' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]        

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
       
        main.step( "Set Cell" )
        main.ONOSbench.setCell(cellName)
        
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
        main.log.info("Startup sequence complete")

        for i in range(5): 
            main.ONOSbench.onosCfgSet(ONOSIp[1], "org.onosproject.fwd.ReactiveForwarding","packetOutOnly true")
            time.sleep(5)
            main.ONOSbench.handle.sendline("onos $OC1 cfg get|grep packetOutOnly") 
            main.ONOSbench.handle.expect(":~") 
            check = main.ONOSbench.handle.before
            if "value=true" in check:
                main.log.info("cfg set successful") 
                break 
            if i == 4: 
                main.log.info("Cfg set failed") 
            else: 
                time.sleep(5)
                
            

        
 
    def CASE2( self, main ):
         
        mode = main.params[ 'TEST' ][ 'mode' ]
        if mode != "t":
            mode = " " 

        runCbench = ( "ssh admin@" + ONOSIp[1] + " cbench -c localhost -p 6633 -m 1000 -l 25 -s 16 -M 100000 -w 15 -D 10000 -" + mode )
        main.ONOSbench.handle.sendline(runCbench)
        time.sleep(30)
        main.ONOSbench.handle.expect(":~") 
        output = main.ONOSbench.handle.before
        main.log.info(output)

        output = output.splitlines()
        for line in output: 
            if "RESULT: " in line: 
                print line
                break 
        
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

        if mode == " ": 
            mode = "l"

        commit = main.ONOSbench.getVersion()
        commit = (commit.split(" "))[1]

        dbfile = open("CbenchBMDB", "w+") 
        temp = "'" + commit + "'," 
        temp += "'" + mode + "'," 
        temp += "'" + avg + "',"
        temp += "'" + stdev + "'\n" 
        dbfile.write(temp)
        dbfile.close()
        main.ONOSbench.logReport(ONOSIp[1], ["ERROR", "WARNING", "EXCEPT"], outputMode="d") 









