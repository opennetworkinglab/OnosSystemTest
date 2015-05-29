
def __init__( self ):
    self.ip = '127.0.0.1'

def getOnosLog( nodeIp, option='grep \'ERROR\' \| \'WARN\'',
        outputType=0):
    """
    Specify grep command to listen for in onos log

    Runs 'onos-check-logs <option>'
    
    outputType
        0: Return output of log
        1: Return (#Errors, #Exceptions, #Warn)

    """
    main.log.info( 'Starting Onos-log listening for '+str(option) )
    if not isinstance( option, basestring ):
        main.log.error( 'Incorrect grep format specified' )
        return main.FALSE

    try:
        cmd = 'onos-check-logs ' + str(nodeIp) + ' | ' + option
        if outputType == 0:
            logResult = main.ONOSnode[0].handle.sendline( cmd )
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


