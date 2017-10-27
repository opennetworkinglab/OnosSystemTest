"""
The functions for intentInstallWithdrawLat

"""
import numpy
import time
import json


def _init_( self ):
    self.default = ''


def sanityCheck( main, linkNumExpected, flowNumExpected, intentNumExpected ):
    """
    Sanity check on numbers of links, flows and intents in ONOS
    """
    attemps = 0
    main.verify = main.FALSE
    linkNum = 0
    flowNum = 0
    intentNum = 0
    while attemps <= main.verifyAttempts:
        time.sleep( main.verifySleep )
        summary = json.loads( main.Cluster.active( 0 ).CLI.summary( timeout=main.timeout ) )
        linkNum = summary.get( "links" )
        flowNum = main.Cluster.active( 0 ).CLI.getTotalFlowsNum( timeout=600, noExit=True )
        intentNum = summary.get( "intents" )
        if linkNum == linkNumExpected and flowNum == flowNumExpected and intentNum == intentNumExpected:
            main.log.info( "links: {}, flows: {}, intents: {}".format( linkNum, flowNum, intentNum ) )
            main.verify = main.TRUE
            break
        attemps += 1
    if not main.verify:
        main.log.warn( "Links or flows or intents number not as expected" )
        main.log.warn( "[Expected] links: {}, flows: {}, intents: {}".format( linkNumExpected, flowNumExpected, intentNumExpected ) )
        main.log.warn( "[Actual]   links: {}, flows: {}, intents: {}".format( linkNum, flowNum, intentNum ) )
        # bring back topology
        bringBackTopology( main )
        if main.validrun >= main.warmUp:
            main.invalidrun += 1
        else:
            main.validrun += 1

def bringBackTopology( main ):
    main.log.info( "Bring back topology " )

    main.Cluster.active( 0 ).CLI.pushTestIntents( main.ingress,
                                                  main.egress,
                                                  main.batchSize,
                                                  offset=1,
                                                  options="-w",
                                                  timeout=main.timeout )
    main.Cluster.active( 0 ).CLI.purgeWithdrawnIntents()
    # configure apps
    main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                         "deviceCount", value=0 )
    main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                         "enabled", value="false" )
    main.Cluster.active( 0 ).CLI.setCfg( main.intentManagerCfg,
                                         "skipReleaseResourcesOnWithdrawal",
                                         value="false" )
    if main.flowObj:
        main.Cluster.active( 0 ).CLI.setCfg( main.intentConfigRegiCfg,
                                             "useFlowObjectives", value="false" )
    time.sleep( main.startUpSleep )
    main.Cluster.active( 0 ).CLI.wipeout()
    time.sleep( main.startUpSleep )
    main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                         "deviceCount", value=main.deviceCount )
    main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                         "enabled", value="true" )
    main.Cluster.active( 0 ).CLI.setCfg( main.intentManagerCfg,
                                         "skipReleaseResourcesOnWithdrawal",
                                         value="true" )
    if main.flowObj:
        main.Cluster.active( 0 ).CLI.setCfg( main.intentConfigRegiCfg,
                                             "useFlowObjectives", value="true" )
    time.sleep( main.startUpSleep )

    # balanceMasters
    main.Cluster.active( 0 ).CLI.balanceMasters()
    time.sleep( main.startUpSleep )
