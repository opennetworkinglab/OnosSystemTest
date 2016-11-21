def addBucket( main , egressPort = "" ):
       """
       Description:
            Create a single bucket which can be added to a Group.
       Optional:
            * egressPort: port of egress device
       Returns:
            * Returns a Bucket
            * Returns None in case of error
       Note:
            The ip and port option are for the requests input's ip and port
            of the ONOS node.
       """
       try:

           bucket = {
                        "treatment":{ "instructions":[] }
                    }
           if egressPort:
               bucket[ 'treatment' ][ 'instructions' ].append( {
                                                        "type":"OUTPUT",
                                                        "port":egressPort } )
           return bucket

       except ( AttributeError, TypeError ):
           main.log.exception( self.name + ": Object not as expected" )
           return None
       except Exception:
           main.log.exception( self.name + ": Uncaught exception!" )
           main.cleanup()
           main.exit()
