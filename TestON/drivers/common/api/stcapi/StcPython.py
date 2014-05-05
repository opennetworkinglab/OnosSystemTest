class StcPython:
    def __init__(self):
        import os
        import sys

        self.stcInt = None

        if sys.hexversion < 0x020605F0 or sys.hexversion > 0x020703F0:
            raise ImportError, "This version of StcPython requires Python version 2.6.5 up to 2.7.3"

        try:
            os.environ['STC_PRIVATE_INSTALL_DIR'] = STC_PRIVATE_INSTALL_DIR
        except:
            raise "Please replace STC_INSTALL_DIR with the actual STC install directory first."

        if os.path.exists(os.environ['STC_PRIVATE_INSTALL_DIR']) == False or \
           os.path.exists(os.path.join(os.environ['STC_PRIVATE_INSTALL_DIR'], 'stcbll.ini')) == False:
            raise ValueError, '%s is not a valid STC install directory.' % (os.environ['STC_PRIVATE_INSTALL_DIR'])

        runningDir = os.getcwd()
        os.chdir(os.environ['STC_PRIVATE_INSTALL_DIR'])
        sys.path.append(os.environ['STC_PRIVATE_INSTALL_DIR'])

        if hex(sys.hexversion).startswith('0x2060'):
            self.stcInt = __import__('StcIntPython')
        else:
            self.stcInt = __import__('StcIntPython27')
            
        os.chdir(runningDir)


    def apply(self):
        return self.stcInt.salApply()

    def config(self, object, **kwargs):
        svec = []
        StcPython.packKeyVal(svec, kwargs)
        return self.stcInt.salSet(object, svec)

    def connect(self, *hosts):
        svec = StcPython.unpackArgs(*hosts)
        return self.stcInt.salConnect(svec)

    def create(self, type, **kwargs):
        svec = []
        if type != "project":
            svec.append("-under")
            svec.append(kwargs.pop("under"))

        StcPython.packKeyVal(svec, kwargs)
        return self.stcInt.salCreate(type, svec)

    def delete(self, handle):
        return self.stcInt.salDelete(handle)

    def disconnect(self, *hosts):
        svec = StcPython.unpackArgs(*hosts)
        return self.stcInt.salDisconnect(svec)

    def get(self, handle, *args):
        svec = StcPython.unpackArgs(*args)
        svecDashes = []
        for i, attName in enumerate(svec):
            svecDashes.append('-' + attName)
        retSvec = self.stcInt.salGet(handle, svecDashes)

        if len(retSvec) == 1:
            return retSvec[0]
        else:
            return StcPython.unpackGetResponseAndReturnKeyVal(retSvec, svec)

    def help(self, topic=""):
        if topic == '' or topic.find(' ') != -1:
            return  "Usage: \n" + \
                    "  stc.help('commands')\n" + \
                    "  stc.help(<handle>)\n" + \
                    "  stc.help(<className>)\n" + \
                    "  stc.help(<subClassName>)"

        if topic == 'commands':
            allCommands = []
            for commandHelp in StcIntPythonHelp.HELP_INFO.values():
                allCommands.append(commandHelp['desc'])
            allCommands.sort()
            return "\n".join(allCommands)

        info = StcIntPythonHelp.HELP_INFO.get(topic)
        if info != None:
            return "Desc: " + info['desc'] + "\n" + \
                   "Usage: " + info['usage'] + "\n" + \
                   "Example: " + info['example'] + "\n"

        return self.stcInt.salHelp(topic)

    def log(self, level, msg):
        return self.stcInt.salLog(level, msg)

    def perform(self, cmd, **kwargs):
        svec = []
        StcPython.packKeyVal(svec, kwargs)
        retSvec = self.stcInt.salPerform(cmd, svec)
        return StcPython.unpackPerformResponseAndReturnKeyVal(retSvec, kwargs.keys())

    def release(self, *csps):
        svec = StcPython.unpackArgs(*csps)
        return self.stcInt.salRelease(svec);

    def reserve(self, *csps):
        svec = StcPython.unpackArgs(*csps)
        return self.stcInt.salReserve(svec);

    def sleep(self, seconds):
        import time
        time.sleep(seconds)

    def subscribe(self, **kwargs):
        svec = []
        StcPython.packKeyVal(svec, kwargs)
        return self.stcInt.salSubscribe(svec)

    def unsubscribe(self, rdsHandle):
        return self.stcInt.salUnsubscribe(rdsHandle)

    def waitUntilComplete(self, **kwargs):
        import os
        import time
        timeout = 0
        if 'timeout' in kwargs:
            timeout = int(kwargs['timeout'])

        sequencer = self.get('system1', 'children-sequencer')

        timer = 0

        while True:
            curTestState = self.get(sequencer, 'state')
            if 'PAUSE' in curTestState or 'IDLE' in curTestState:
                break

            time.sleep(1)
            timer += 1

            if timeout > 0 and timer > timeout:
                raise Exception, "ERROR: Stc.waitUntilComplete timed out after %s sec" % timeout

        if 'STC_SESSION_SYNCFILES_ON_SEQ_COMPLETE' in os.environ and \
            os.environ['STC_SESSION_SYNCFILES_ON_SEQ_COMPLETE'] == "1" and \
            self.perform('CSGetBllInfo')['ConnectionType'] == 'SESSION':
                self.perform('CSSynchronizeFiles')

        return self.get(sequencer, 'testState')

    @staticmethod
    def unpackArgs(*args):
         import types
         svec = []
         for arg in args:
            if type(arg) is types.ListType:
                svec.extend(arg)
            else:
                svec.append(arg)
         return svec

    @staticmethod
    def packKeyVal(svec, hash):
        import types
        for key, val in hash.iteritems():
            svec.append('-' + str(key))
            if type(val) is types.ListType:
                svec.append(' '.join(map(str, val)))
            else:
                svec.append(str(val));

    @staticmethod
    def unpackGetResponseAndReturnKeyVal(svec, origKeys):
        useOrigKey = len(origKeys) == len(svec)/2
        hash = dict()
        for i in range(0, (len(svec)/2)):
            key = svec[i*2]
            key = key[1:len(key)]
            val = svec[i*2+1]
            if useOrigKey:
                key = origKeys[i]
            hash[key] = val
        return hash

    @staticmethod
    def unpackPerformResponseAndReturnKeyVal(svec, origKeys):
        origKeyHash = dict()
        for key in origKeys:
            origKeyHash[key.lower()] = key

        hash = dict()
        for i in range(0, (len(svec)/2)):
            key = svec[i*2]
            key = key[1:len(key)]
            val = svec[i*2+1]
            if key.lower() in origKeyHash:
                key = origKeyHash[key.lower()]
            hash[key] = val
        return hash

# internal help info
class StcIntPythonHelp:

    def __init__(self):
        pass

    HELP_INFO = dict(    create =            dict(desc    = "create: -Creates an object in a test hierarchy",
                                                  usage   = "stc.create( className, under = parentObjectHandle, propertyName1 = propertyValue1, ... )",
                                                  example = 'stc.create( \'port\', under=\'project1\', location = "#{mychassis1}/1/2" )'),

                         config =            dict(desc    = "config: -Sets or modifies the value of an attribute",
                                                  usage   = "stc.config( objectHandle, propertyName1 = propertyValue1, ... )",
                                                  example = "stc.config( stream1, enabled = true )"),

                         get =               dict(desc    = "get: -Retrieves the value of an attribute",
                                                  usage   = "stc.get( objectHandle, propertyName1, propertyName2, ... )",
                                                  example = "stc.get( stream1, 'enabled', 'name' )"),

                         perform =           dict(desc    = "perform: -Invokes an operation",
                                                  usage   = "stc.perform( commandName, propertyName1 = propertyValue1, ... )",
                                                  example = "stc.perform( 'createdevice', parentHandleList = 'project1' createCount = 4 )"),

                         delete  =           dict(desc    = "delete: -Deletes an object in a test hierarchy",
                                                  usage   = "stc.delete( objectHandle )",
                                                  example = "stc.delete( stream1 )"),

                         connect =           dict(desc    = "connect: -Establishes a connection with a Spirent TestCenter chassis",
                                                  usage   = "stc.connect( hostnameOrIPaddress, ... )",
                                                  example = "stc.connect( mychassis1 )"),

                         disconnect =        dict(desc    = "disconnect: -Removes a connection with a Spirent TestCenter chassis",
                                                  usage   = "stc.disconnect( hostnameOrIPaddress, ... )" ,
                                                  example = "stc.disconnect( mychassis1 )") ,

                         reserve =           dict(desc    = "reserve: -Reserves a port group",
                                                  usage   = "stc.reserve( CSP1, CSP2, ... )",
                                                  example = 'stc.reserve( "//#{mychassis1}/1/1", "//#{mychassis1}/1/2" )'),

                         release =           dict(desc    = "release: -Releases a port group",
                                                  usage   = "stc.release( CSP1, CSP2, ... )",
                                                  example = 'stc.release( "//#{mychassis1}/1/1", "//#{mychassis1}/1/2" )'),

                         apply =             dict(desc    = "apply: -Applies a test configuration to the Spirent TestCenter firmware",
                                                  usage   = "stc.apply()",
                                                  example = "stc.apply()"),

                         log  =              dict(desc    = "log: -Writes a diagnostic message to the log file",
                                                  usage   = "stc.log( logLevel, message )",
                                                  example = "stc.log( 'DEBUG', 'This is a debug message' )"),

                         waitUntilComplete = dict(desc    = "waitUntilComplete: -Suspends your application until the test has finished",
                                                  usage   = "stc.waitUntilComplete()",
                                                  example = "stc.waitUntilComplete()"),

                         subscribe =         dict(desc    = "subscribe: -Directs result output to a file or to standard output",
                                                  usage   = "stc.subscribe( parent=parentHandle, resultParent=parentHandles, configType=configType, resultType=resultType, viewAttributeList=attributeList, interval=interval, fileNamePrefix=fileNamePrefix )",
                                                  example = "stc.subscribe( parent='project1', configType='Analyzer', resulttype='AnalyzerPortResults', filenameprefix='analyzer_port_counter' )"),

                         unsubscribe =       dict(desc    = "unsubscribe: -Removes a subscription",
                                                  usage   = "stc.unsubscribe( resultDataSetHandle )",
                                                  example = "stc.unsubscribe( resultDataSet1 )"))
