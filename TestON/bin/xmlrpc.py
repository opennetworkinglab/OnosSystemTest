from SimpleXMLRPCServer import SimpleXMLRPCServer
from xmlrpclib import Binary
import datetime

server = SimpleXMLRPCServer(('localhost', 9000), logRequests=True, allow_none=True)
server.register_introspection_functions()
server.register_multicall_functions()
import sys
import inspect
from cli import * 

from cli import CLI
cliObj = CLI("test")
import threading
from cli import TestThread
import __builtin__
__builtin__.testthread = False
sys.path.append("../")
from core import xmldict

class ExampleService:
    thread = threading.Thread()     
    def ping(self):
        """Simple function to respond when called to demonstrate connectivity."""


        return True
        
    def now(self):
        """Returns the server current date and time."""
        return datetime.datetime.now()

    def show_type(self, arg):
        """Illustrates how types are passed in and out of server methods.
        
        Accepts one argument of any type.  
        Returns a tuple with string representation of the value, 
        the name of the type, and the value itself.
        """
        return (str(arg), str(type(arg)), arg)

    def raises_exception(self, msg):
        "Always raises a RuntimeError with the message passed in"
        raise RuntimeError(msg)

    def send_back_binary(self, bin):
        "Accepts single Binary argument, unpacks and repacks it to return it"
        data = bin.data
        response = Binary(data)
        return response

    def stop(self):
        cliObj.do_stop("Enter")        
  
    def runTest(self,testName) :

        testthread = cliObj.do_run(testName)
        import time
        time.sleep(1) 
        log =  cliObj.getlog()  
        print log 
        return log

    def pauseTest(self):
        testthread.pause()
        return "Will pause the test's execution, after completion of this step....."        

    def dumpVar(self,variable): 
        var1 = cliObj.do_dumpvar(variable)
    
        return var1
 
    def currentStep(self):
        return cliObj.do_currentstep("Test") 
    
    def currentCase(self):
        return cliObj.do_currentcase("Test")

    def showLog(self):
        return cliObj.do_showlog("Test")

    def nextStep(self):
        cliObj.do_nextstep("Test")

    def resume(self):
        cliObj.do_resume("Test")

    def doCommand(self,line):
        return cliObj.do_do(line) 

    def interpret(self,line):
        return cliObj.do_interpret(line)    
    
    def doCompile(self,line):
        return cliObj.do_compile(line)

    def getTest(self):
        return cliObj.do_gettest("Test")          

    def getLog(self):
        return cliObj.getlog()  

    def reverseCompile(self,line):
        return cliObj.do_reverse(line)

    def getDict(self,fileName):
        dictionary = self.parse(fileName)
        print dictionary  
        return dictionary 

    def parse(self,fileName) :
        '''
         This will parse the params or topo or cfg file and return content in the file as Dictionary
        '''
        self.fileName = fileName
        matchFileName = re.match("(.*)\.(params|topo|cfg)", self.fileName, re.M | re.I)
        print matchFileName.group(1)  
        if matchFileName:
            xml = open(fileName).read()
            parsedInfo = xmldict.xml_to_dict(xml) 
            return parsedInfo

        else :
            print "file name is not correct"
     
       
server.register_instance(ExampleService())

try:
    print 'Use Control-C to exit'
    server.serve_forever()
except KeyboardInterrupt:
    print 'Exiting'