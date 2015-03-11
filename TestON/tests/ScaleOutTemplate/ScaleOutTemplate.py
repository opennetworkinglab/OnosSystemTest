# ScaleOutTemplate
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os.path


class ScaleOutTemplate:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):            #This is the initialization case
                                        #this case will clean up all nodes 
        import time                     #but only node 1 is started in this case
        
        global clusterCount             #number of nodes running
        global ONOSIp                   #list of ONOS IP addresses 
        clusterCount = 1
        ONOSIp = [ 0 ]


        #Load values from params file
        checkoutBranch = main.params[ 'GIT' ][ 'checkout' ]
        gitPull = main.params[ 'GIT' ][ 'autopull' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        Features= main.params[ 'ENV' ][ 'cellFeatures' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        maxNodes = int(main.params[ 'availableNodes' ])
        Features = main.params[ 'ENV' ][ 'cellFeatures' ]
        skipMvn = main.params[ 'TEST' ][ 'skipCleanInstall' ]

        #Populate ONOSIp with ips from params 
        for i in range(1, maxNodes + 1): 
            ipString = 'ip' + str(i) 
            ONOSIp.append(main.params[ 'CTRL' ][ ipString ])   

        #############################
        tempIp = [ ONOSIp[1],ONOSIp[2],ONOSIp[3],ONOSIp[4],ONOSIp[5]]
        main.ONOSbench.createLinkGraphFile(BENCHIp, tempIp, str(7)) 

        main.log.info("marker")
        #############################


        #kill off all onos processes 
        main.log.step("Safety check, killing all ONOS processes")
        main.log.step("before initiating enviornment setup")
        for node in range(1, maxNodes + 1):
            main.ONOSbench.onosDie(ONOSIp[node])


        #construct the cell file
        main.log.info("Creating cell file")
        exec "a = main.ONOSbench.createCellFile"
        cellIp = []
        for node in range (1, maxNodes + 1):
            cellIp.append(ONOSIp[node])
        a(BENCHIp,cellName,MN1Ip,str(Features), *cellIp)

        #Uninstall everywhere
        main.log.step( "Cleaning Enviornment..." )
        for i in range(1, maxNodes + 1):
            main.log.info(" Uninstalling ONOS " + str(i) )
            main.ONOSbench.onosUninstall( ONOSIp[i] )
        
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


        #main.step( "Set cell for ONOS cli env" )
        #main.ONOS1cli.setCell( cellName )
        
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()  

        main.step( "Installing ONOS package" )
        install1Result = main.ONOSbench.onosInstall( node=ONOSIp[1] )

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        main.step( "Applying cell file to environment" )
        cellApplyResult = main.ONOSbench.setCell( cellName )
        main.step( "verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()

        main.step( "Set cell for ONOS cli env" )
        cli1 = main.ONOS1cli.startOnosCli( ONOSIp[1] )

        
    def CASE2( self, main ):
        # This case increases the cluster size by whatever scale is
        # Note: 'scale' is the size of the step
        # if scaling is not a part of your test, simply run this case
        # once after CASE1 to set up your enviornment for your desired 
        # cluster size. If scaling is a part of you test call this case each time 
        # you want to increase cluster size

        ''                                                         
        'Increase number of nodes and initiate CLI'
        ''
        import time
        global clusterCount
        
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        scale = int( main.params[ 'SCALE' ] )
        clusterCount += scale

        main.log.report( "Increasing cluster size to " + str( clusterCount ) )
        for node in range((clusterCount - scale) + 1, clusterCount + 1):
            main.ONOSbench.onosDie(ONOSIp[node])
            time.sleep(10)
            main.log.info("Starting ONOS " + str(node) + " at IP: " + ONOSIp[node])    
            main.ONOSbench.onosInstall( node=ONOSIp[node])
            exec "a = main.ONOS%scli.startOnosCli" %str(node)
            a(ONOSIp[node])
         

