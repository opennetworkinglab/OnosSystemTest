import json
import time
class CheckingFlow:

    def __init__( self ):
        self.default = ''

    def checkFlow( self ):
        main.step("Check flow is in the ADDED state")
        main.log.info( "Get the flows from ONOS" )
        try:
            flows = json.loads( main.ONOSrest.flows() )

            stepResult = main.TRUE
            for f in flows:
                if "rest" in f.get( "appId" ):
                    if "ADDED" not in f.get( "state" ):
                        stepResult = main.FALSE
                        main.log.error( "Flow: %s in state: %s" % ( f.get( "id" ), f.get( "state" ) ) )
        except TypeError:
            main.log.error( "No Flows found by the REST API" )
            stepResult = main.FALSE
        except ValueError:
            main.log.error( "Problem getting Flows state from REST API.  Exiting test" )
            main.cleanup()
            main.exit()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in the ADDED state",
                                 onfail="All flows are NOT in the ADDED state" )

        main.step( "Check flows are in Mininet's flow table" )

        # get the flow IDs that were added through rest
        main.log.info( "Getting the flow IDs from ONOS" )
        flowIds = [ f.get( "id" ) for f in flows if "rest" in f.get( "appId" ) ]
        # convert the flowIDs to ints then hex and finally back to strings
        flowIds = [ str( hex( int( x ) ) ) for x in flowIds ]
        main.log.info( "ONOS flow IDs: {}".format( flowIds ) )

        stepResult = main.Mininet1.checkFlowId( "s1", flowIds, debug=False )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in mininet",
                                 onfail="All flows are NOT in mininet" )
