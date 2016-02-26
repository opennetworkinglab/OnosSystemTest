"""
Start CLI for CHOTestMonkey
Author: you@onlab.us
"""
from multiprocessing.connection import Client

commandMap = {}
paramNum = {}

def triggerEvent( debugMode, name, scheduleMethod, args ):
    """
    This function inserts an event from CLI to CHOTestMonkey
    """
    host = "localhost"
    port = 6000
    address = ( host, port )
    conn = Client( address )
    request = []
    if debugMode:
        request.append( 2 )
    else:
        request.append( 1 )
    request.append( name )
    request.append( scheduleMethod )
    for arg in args:
        request.append( arg )
    conn.send( request )
    response = conn.recv()
    return response

def startCLI():
    debugMode = False
    while 1:
        try:
            if debugMode:
                cmd = raw_input("CHOTestMonkey-debug>")
            else:
                cmd = raw_input("CHOTestMonkey>")
        except EOFError:
            print "exit"
            return
        except Exception:
            print "Uncaught exception!"
            return

        if cmd == 'help':
            print 'Supported commands:'
            print 'help'
            print 'debug'
            print 'exit'
            for command in commandMap.keys():
                print command
        elif cmd == '':
            pass
        elif cmd == 'debug':
            debugMode = True
        elif cmd == 'exit':
            if debugMode:
                debugMode = False
            else:
                return
        else:
            cmdList = cmd.split( ' ' )
            if cmdList[ 0 ] in commandMap.keys():
                num = paramNum[ cmdList[ 0 ] ]
                name = commandMap[ cmdList[ 0 ] ]
                if len( cmdList ) < num + 1:
                    print 'not enough arguments'
                elif len( cmdList ) > num + 1:
                    print 'Too many arguments'
                else:
                    result = triggerEvent( debugMode, name, 'RUN_BLOCK', cmdList[ 1: ] )
                    if result == 10:
                        pass
                    elif result == 11:
                        print "Scheduler busy...Try later or use debugging mode by entering \'debug\'"
                    elif result == 20:
                        print "Unknown message to server"
                    elif result == 21:
                        print "Unknown event type to server"
                    elif result == 22:
                        print "Unknown schedule method to server"
                    elif result == 23:
                        print "Not enough argument"
                    else:
                        print "Unknown response from server"
            else:
                print 'Unknown command'

if __name__ == '__main__':
    import xml.etree.ElementTree
    try:
        root = xml.etree.ElementTree.parse( '../CHOTestMonkey.params' ).getroot()
    except Exception:
        print "Uncaught exception!"
    for child in root:
        if child.tag == 'EVENT':
            for event in child:
                for item in event:
                    if item.tag == 'CLI':
                        CLI = str( item.text )
                    if item.tag == 'typeString':
                        name = str( item.text )
                    if item.tag == 'CLIParamNum':
                        num = int( item.text )
                commandMap[ CLI ] = name
                paramNum[ CLI ] = num
    startCLI()

