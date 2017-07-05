"""
    These functions can be used for topology comparisons
"""

import time
import os
import json

def sendArpPackage( main, hostList ):
    import json
    import time
    """
        send arping package from host
        return the total hosts number from Onos
    """
    main.log.info( "Sending Arping package..." )
    if isinstance(hostList, list):
        for h in hostList:
            main.Mininet1.arping( srcHost=h, dstHost="10.0.0.1", output=main.FALSE, noResult=True )
            time.sleep(0.5)
    else:
        main.Mininet1.arping( srcHost=hostList, dstHost="10.0.0.1", output=main.FALSE, noResult=True )
    try:
        summaryStr = ""
        summaryStr = json.loads( main.CLIs[0].summary().encode() )
        hostNum = summaryStr.get( 'hosts' )

    except (TypeError, ValueError):
        main.log.exception( " Object not as expected: {!r}".format( summaryStr) )
        return -1
    except Exception:
        main.log.exception( self.name + ": Uncaught exception!" )
        return -1

    return hostNum
