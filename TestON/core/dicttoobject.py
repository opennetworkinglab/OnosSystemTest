#!/usr/bin/env python

class DictToObject( dict ):
    def __init__( self, data = None ):
        super( DictToObject, self ).__init__()
        if data:
            self.__update( data, {} )

    def __update( self, data, did ):
        dataid = id(data)
        did[ dataid ] = self

        for k in data:
            dkid = id(data[k])
            if did.has_key(dkid):
                self[k] = did[dkid]
            elif isinstance( data[k], DictToObject ):
                self[k] = data[k]
            elif isinstance( data[k], dict ):
                obj = DictToObject()
                obj.__update( data[k], did )
                self[k] = obj
                obj = None
            else:
                self[k] = data[k]

    def __getattr__( self, key ):
        return self.get( key, None )

    def __setattr__( self, key, value ):
        if isinstance(value,dict):
            self[key] = DictToObject( value )
        else:
            self[key] = value

    def update( self, *args ):
        for obj in args:
            for k in obj:
                if isinstance(obj[k],dict):
                    self[k] = DictToObject( obj[k] )
                else:
                    self[k] = obj[k]
        return self

    def merge( self, *args ):
        for obj in args:
            for k in obj:
                if self.has_key(k):
                    if isinstance(self[k],list) and isinstance(obj[k],list):
                        self[k] += obj[k]
                    elif isinstance(self[k],list):
                        self[k].append( obj[k] )
                    elif isinstance(obj[k],list):
                        self[k] = [self[k]] + obj[k]
                    elif isinstance(self[k],DictToObject) and isinstance(obj[k],Object):
                        self[k].merge( obj[k] )
                    elif isinstance(self[k],DictToObject) and isinstance(obj[k],dict):
                        self[k].merge( obj[k] )
                    else:
                        self[k] = [ self[k], obj[k] ]
                else:
                    if isinstance(obj[k],dict):
                        self[k] = DictToObject( obj[k] )
                    else:
                        self[k] = obj[k]
        return self
    
