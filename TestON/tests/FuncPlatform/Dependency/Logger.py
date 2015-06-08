
def __init__( self ):
    self.ip = '127.0.0.1'

def checkOnosLog( nodeIp, option='',
        outputType=0):
    """
    Listens to the log for any Errors and Exceptions.

    Runs 'onos-check-logs <option>'
    This script only returns if there are any errors
    or exceptions

    outputType
        0: Return output of log
        1: Return (#Errors, #Exceptions, #Warn)

    """
    if not isinstance( option, basestring ):
        main.log.error( 'Incorrect grep format specified' )
        return main.FALSE

    try:
        main.log.info( 'Starting Onos-log listening for '+
                str(option) )
        cmd = 'onos-check-logs ' + str(nodeIp) + ' old'
        if outputType == 0:
            main.ONOSbench.handle.sendline( cmd )
            main.ONOSbench.handle.expect( cmd )
            main.ONOSbench.handle.expect('\$')
            logResult = main.ONOSbench.handle.before
            return logResult
        elif outputType == 1:
            # Important in assertion criteria
            # to determine how much warn / error is 
            # acceptable
            return 'Implement option 1'
        else:
            main.log.error( 'Incorrect outputType specified' )
            return main.FALSE

    except Exception:
        main.log.exception( self.name + ': Uncaught exception' ) 
        main.cleanup()
        main.exit()

def setLogLevel( level ):
    """
    Set the log level of onos
    """
    main.log.info( 'setLogLevel implement me' )

def getLogReport( nodeIp, searchTerms ):
    """
    Refer to CLI driver for 'logReport'
    """
    main.log.info( 'getLogReport - implement me!' )
