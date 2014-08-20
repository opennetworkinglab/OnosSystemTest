#!/usr/bin/env python
'''
Created on 22-Oct-2012
    
@author: Anil Kumar (anilkumar.s@paxterrasolutions.com)


    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.		



teston is the main module.

'''

import sys
import getpass
import os
import re
import __builtin__
import new
import xmldict
module = new.module("test")
import openspeak
global path, drivers_path, core_path, tests_path,logs_path
path = re.sub("(core|bin)$", "", os.getcwd())
drivers_path = path+"drivers/"
core_path = path+"core"
tests_path = path+"tests"
logs_path = path+"logs/"
config_path = path + "config/"
sys.path.append(path)
sys.path.append( drivers_path)
sys.path.append(core_path )
sys.path.append(tests_path)

from core.utilities import Utilities

import logging 
import datetime
from optparse import OptionParser

class TestON:
    '''
    
    TestON will initiate the specified test. 
    The main tasks are : 
    * Initiate the required Component handles for the test. 
    * Create Log file  Handles.
    
    '''
    def __init__(self,options):
        '''
           Initialise the component handles specified in the topology file of the specified test.
          
        '''
        # Initialization of the variables.
        __builtin__.main = self
        
        __builtin__.path = path
        __builtin__.utilities = Utilities()
        self.TRUE = 1
        self.FALSE = 0
        self.ERROR = -1
        self.FAIL = False
        self.PASS = True
        self.CASERESULT = self.TRUE
        self.init_result = self.TRUE
        self.testResult = "Summary"
        self.stepName =""
        self.EXPERIMENTAL_MODE = False   
        self.test_target = None
        self.lastcommand = None
        self.testDir = tests_path 
        self.configFile = config_path + "teston.cfg" 
        self.parsingClass = "xmlparser"
        self.parserPath = core_path + "/xmlparser"
        self.loggerPath = core_path + "/logger"
        self.loggerClass = "Logger"
        self.logs_path = logs_path
        self.driver = ''
	
        
        self.configparser()
        verifyOptions(options)
        load_logger()
        self.componentDictionary = {}
        self.componentDictionary = self.topology ['COMPONENT']
        self.driversList=[]
        if type(self.componentDictionary) == str :
            self.componentDictionary = dict(self.componentDictionary)
            
        for component in self.componentDictionary :
            self.driversList.append(self.componentDictionary[component]['type'])
            
        self.driversList = list(set(self.driversList)) # Removing duplicates.
        # Checking the test_target option set for the component or not
        if type(self.componentDictionary) == dict:
            for component in self.componentDictionary.keys():
                if 'test_target' in self.componentDictionary[component].keys():
                    self.test_target = component
             
        # Checking for the openspeak file and test script 
        self.logger.initlog(self)

        # Creating Drivers Handles
        initString = "\n"+"*" * 30+"\n CASE INIT \n"+"*" * 30+"\n"
        self.log.exact(initString)
        self.driverObject = {}
        self.random_order = 111 # Random order id to connect the components
        components_connect_order = {}
        #component_list.append()
        if type(self.componentDictionary) == dict:
            for component in self.componentDictionary.keys():
                self.componentDictionary[component]['connect_order'] = self.componentDictionary[component]['connect_order'] if ('connect_order' in self.componentDictionary[component].keys()) else str(self.get_random())
                components_connect_order[component] =  eval(self.componentDictionary[component]['connect_order'])
            #Ordering components based on the connect order.
            ordered_component_list =sorted(components_connect_order, key=lambda key: components_connect_order[key])
            print ordered_component_list
            
            for component in ordered_component_list:
                self.componentInit(component)

    def configparser(self):
        '''
        It will parse the config file (teston.cfg) and return as dictionary
        '''
        matchFileName = re.match(r'(.*)\.cfg', self.configFile, re.M | re.I)
        if matchFileName:
            xml = open(self.configFile).read()
            try :
                self.configDict = xmldict.xml_to_dict(xml)
                return self.configDict
            except :
                print "There is no such file to parse " + self.configFile
                        
    def componentInit(self,component):
        '''
        This method will initialize specified component
        '''
        global driver_options
        self.log.info("Creating component Handle: "+component)
        driver_options = {}         
        if 'COMPONENTS' in self.componentDictionary[component].keys():
            driver_options =dict(self.componentDictionary[component]['COMPONENTS'])

        driver_options['name']=component
        driverName = self.componentDictionary[component]['type']
        driver_options ['type'] = driverName
        
        classPath = self.getDriverPath(driverName.lower())
        driverModule = __import__(classPath, globals(), locals(), [driverName.lower()], -1)
        driverClass = getattr(driverModule, driverName)
        driverObject = driverClass()
         
        connect_result = driverObject.connect(user_name = self.componentDictionary[component]['user'] if ('user' in self.componentDictionary[component].keys()) else getpass.getuser(),
                                              ip_address= self.componentDictionary[component]['host'] if ('host' in self.componentDictionary[component].keys()) else 'localhost',
                                              pwd = self.componentDictionary[component]['password'] if ('password' in self.componentDictionary[component].keys()) else 'changeme',
                                              port = self.componentDictionary[component]['port'] if ('port' in self.componentDictionary[component].keys()) else None,
                                              options = driver_options)
        if not connect_result:
            self.log.error("Exiting form the test execution because the connecting to the "+component+" component failed.")
            self.exit() 
            
        vars(self)[component] = driverObject
                        
    def run(self):
        '''
           The Execution of the test script's cases listed in the Test params file will be done here. 
           And Update each test case result. 
           This method will return TRUE if it executed all the test cases successfully, 
           else will retun FALSE
        '''
        
        self.testCaseResult = {}
        self.TOTAL_TC = 0
        self.TOTAL_TC_RUN = 0
        self.TOTAL_TC_PLANNED = 0 
        self.TOTAL_TC_NORESULT = 0
        self.TOTAL_TC_FAIL = 0
        self.TOTAL_TC_PASS = 0
        self.TEST_ITERATION = 0
        self.stepCount = 0
        self.CASERESULT = self.TRUE
        
        import testparser 
        testFile = self.tests_path + "/"+self.TEST + "/"+self.TEST + ".py"
        test = testparser.TestParser(testFile)
        self.testscript = test.testscript
        self.code = test.getStepCode()
	repeat= int(self.params['repeat']) if ('repeat' in self.params) else 1
	main.TOTAL_TC_PLANNED = len(self.testcases_list)*repeat
        
        result = self.TRUE
	while(repeat):
            for self.CurrentTestCaseNumber in self.testcases_list:
                result = self.runCase(self.CurrentTestCaseNumber) 
	    repeat-=1                   
        return result
    
    def runCase(self,testCaseNumber):
        self.CurrentTestCaseNumber = testCaseNumber
        result = self.TRUE
        self.stepCount = 0
        self.EXPERIMENTAL_MODE = self.FALSE
        self.addCaseHeader()
        self.testCaseNumber = str(testCaseNumber)
        stopped = False
        try :
            self.stepList = self.code[self.testCaseNumber].keys()
        except KeyError,e:
            main.log.error("There is no Test-Case "+ self.testCaseNumber)
            return main.FALSE
        
        self.stepCount = 0
        while self.stepCount < len(self.code[self.testCaseNumber].keys()):
            result = self.runStep(self.stepList,self.code,self.testCaseNumber)
            if result == main.FALSE:
                break
            elif result == main.TRUE :
                continue
            
        if not stopped :
            self.testCaseResult[str(self.CurrentTestCaseNumber)] = self.CASERESULT
            self.logger.updateCaseResults(self)
        return result
    
    def runStep(self,stepList,code,testCaseNumber):
        if not cli.pause:
            try :
                step = stepList[self.stepCount]
                exec code[testCaseNumber][step] in module.__dict__
                self.stepCount = self.stepCount + 1
            except TypeError,e:
                self.stepCount = self.stepCount + 1
                self.log.error(e)
            return main.TRUE
        
        if cli.stop:
            cli.stop = False
            stopped = True
            self.TOTAL_TC_NORESULT = self.TOTAL_TC_NORESULT + 1
            self.testCaseResult[str(self.CurrentTestCaseNumber)] = "Stopped"
            self.logger.updateCaseResults(self)
            result = self.cleanup()
            return main.FALSE
        
    def addCaseHeader(self):
        caseHeader = "\n"+"*" * 30+"\n Result summary for Testcase"+str(self.CurrentTestCaseNumber)+"\n"+"*" * 30+"\n"
        self.log.exact(caseHeader) 
        caseHeader = "\n"+"*" * 40 +"\nStart of Test Case"+str(self.CurrentTestCaseNumber)+" : " 
        for driver in self.componentDictionary.keys():
            vars(self)[driver+'log'].info(caseHeader)
    
    def addCaseFooter(self):
        if self.stepCount-1 > 0 :
            previousStep = " "+str(self.CurrentTestCaseNumber)+"."+str(self.stepCount-1)+": "+ str(self.stepName) + ""
            stepHeader = "\n"+"*" * 40+"\nEnd of Step "+previousStep+"\n"+"*" * 40+"\n"
            
        caseFooter = "\n"+"*" * 40+"\nEnd of Test case "+str(self.CurrentTestCaseNumber)+"\n"+"*" * 40+"\n"
            
        for driver in self.driversList:
            vars(self)[driver].write(stepHeader+"\n"+caseFooter)

    def cleanup(self):
        '''
           Release all the component handles and the close opened file handles.
           This will return TRUE if all the component handles and log handles closed properly,
           else return FALSE

        '''
        result = self.TRUE
        self.logger.testSummary(self)
        
        #self.reportFile.close()
        

        #utilities.send_mail()
        try :
            for component in self.componentDictionary.keys():
                tempObject  = vars(self)[component]    
                print "Disconnecting "+str(tempObject)
         
                tempObject.disconnect()
            #tempObject.execute(cmd="exit",prompt="(.*)",timeout=120) 

        except(Exception):
            #print " There is an error with closing hanldes"
            result = self.FALSE
        # Closing all the driver's session files
        for driver in self.componentDictionary.keys():
           vars(self)[driver].close_log_handles()
           
        return result
        
    def pause(self):
        '''
        This function will pause the test's execution, and will continue after user provide 'resume' command.
        '''
        __builtin__.testthread.pause()
    
    def onfail(self,*components):
        '''
        When test step failed, calling all the components onfail. 
        '''
         
        if not components:
            try :
                for component in self.componentDictionary.keys():
                    tempObject  = vars(self)[component]
                    result = tempObject.onfail()
            except(Exception),e:
                print str(e)
                result = self.FALSE
                
        else:
            try :
                for component in components:
                    tempObject  = vars(self)[component]
                    result = tempObject.onfail()
            except(Exception),e:
                print str(e)
                result = self.FALSE
    
    
    def getDriverPath(self,driverName):
        '''
           Based on the component 'type' specified in the params , this method will find the absolute path ,
           by recursively searching the name of the component.
        '''
        import commands

        cmd = "find "+drivers_path+" -name "+driverName+".py"
        result = commands.getoutput(cmd)
        
        result_array = str(result).split('\n')
        result_count = 0
        
        for drivers_list in result_array:
            result_count = result_count+1
        if result_count > 1 :
            print "found "+driverName+" "+ str(result_count) + "  times"+str(result_array)
            self.exit()
            
        result = re.sub("(.*)drivers","",result)
        result = re.sub("\.py","",result)
        result = re.sub("\.pyc","",result)
        result = re.sub("\/",".",result)
        result = "drivers"+result
        return result
    

    def step(self,stepDesc):
        '''
           The step information of the test-case will append to the logs.
        '''
        previousStep = " "+str(self.CurrentTestCaseNumber)+"."+str(self.stepCount-1)+": "+ str(self.stepName) + ""
        self.stepName = stepDesc

        stepName = " "+str(self.CurrentTestCaseNumber)+"."+str(self.stepCount)+": "+ str(stepDesc) + ""
        try :
            if self.stepCount == 0:
                stepName = " INIT : Initializing the test case :"+self.CurrentTestCase
        except AttributeError:
                stepName = " INIT : Initializing the test case :"+str(self.CurrentTestCaseNumber)
            
        self.log.step(stepName)
        stepHeader = ""
        if self.stepCount > 1 :
            stepHeader = "\n"+"-"*45+"\nEnd of Step "+previousStep+"\n"+"-"*45+"\n"
        
        stepHeader += "\n"+"-"*45+"\nStart of Step"+stepName+"\n"+"-"*45+"\n" 
        for driver in self.componentDictionary.keys():
            vars(self)[driver+'log'].info(stepHeader)
            
    def case(self,testCaseName):
        '''
           Test's each test-case information will append to the logs.
        '''
        self.CurrentTestCase = testCaseName 
        testCaseName = " " + str(testCaseName) + ""
        self.log.case(testCaseName)
        caseHeader = testCaseName+"\n"+"*" * 40+"\n" 
        for driver in self.componentDictionary.keys():
            vars(self)[driver+'log'].info(caseHeader)
        
    def testDesc(self,description):
        '''
           Test description will append to the logs.
        '''
        description = "Test Description : " + str (description) + ""
        self.log.info(description)
        
    def _getTest(self):
        '''
           This method will parse the test script to find required test information.
        '''
        testFile = self.tests_path + "/"+self.TEST + "/"+self.TEST + ".py"
        testFileHandler = open(testFile, 'r')
        testFileList = testFileHandler.readlines()
        testFileHandler.close()
        #self.TOTAL_TC_PLANNED = 0
        counter = 0
        for index in range(len(testFileList)):
            lineMatch = re.match('\s+def CASE(\d+)(.*):',testFileList[index],0)
            if lineMatch:
                counter  = counter + 1
                self.TC_PLANNED = len(self.testcases_list)
        
                
    def response_parser(self,response, return_format):
        ''' It will load the default response parser '''
        response_dict = {}
        response_dict = self.response_to_dict(response, return_format)
        return_format_string = self.dict_to_return_format(response,return_format,response_dict)   
        return return_format_string
    
    def response_to_dict(self,response,return_format):
        
        response_dict = {}
        json_match = re.search('^\s*{', response)
        xml_match = re.search('^\s*\<', response)
        ini_match = re.search('^\s*\[', response)
        if json_match :
            main.log.info(" Response is in 'JSON' format and Converting to '"+return_format+"' format")
            # Formatting the json string 
            
            response = re.sub(r"{\s*'?(\w)", r'{"\1', response)
            response = re.sub(r",\s*'?(\w)", r',"\1', response)
            response = re.sub(r"(\w)'?\s*:", r'\1":', response)
            response = re.sub(r":\s*'(\w)'\s*([,}])", r':"\1"\2', response)
            
            try :
                import json
                response_dict = json.loads(response)
            except Exception , e :
                print e
                main.log.error("Json Parser is unable to parse the string")
            return response_dict
        
        elif ini_match :
            main.log.info(" Response is in 'INI' format and Converting to '"+return_format+"' format")
            from configobj import ConfigObj
            response_file = open("respnse_file.temp",'w')
            response_file.write(response)
            response_file.close() 
            response_dict = ConfigObj("respnse_file.temp")
            return response_dict
            
        elif xml_match :
            main.log.info(" Response is in 'XML' format and Converting to '"+return_format+"' format")
            try :
                from core import dicttoobject
                response_dict = xmldict.xml_to_dict("<response> "+str(response)+" </response>")
            except Exception, e:
                main.log.error(e)
            return response_dict
        
    def dict_to_return_format(self,response,return_format,response_dict):
        
        if return_format =='table' :
            ''' Will return in table format'''
            to_do = "Call the table output formatter"
            global response_table
            response_table = '\n'
            response_table = response_table +'\t'.join(response_dict)+"\n"
            
            def get_table(value_to_convert):
                ''' This will parse the dictionary recusrsively and print as table format'''
                table_data = ""
                if type(value_to_convert) == dict :
                    table_data = table_data +'\t'.join(value_to_convert)+"\n"
                    for temp_val in value_to_convert.values() :
                        table_data = table_data + get_table(temp_val)
                else :
                    table_data = table_data + str(value_to_convert) +"\t"
                return table_data 
            
            for value in response_dict.values() :
                response_table =  response_table + get_table(value)
                

                
            #response_table = response_table + '\t'.join(response_dict.values())
                
            return response_table
        
        elif return_format =='config':
            ''' Will return in config format'''
            to_do = 'Call dict to config coverter'
            response_string = str(response_dict)
            print response_string
            response_config = re.sub(",", "\n\t", response_string)
            response_config = re.sub("u\'", "\'", response_config)
            response_config = re.sub("{", "", response_config)
            response_config = re.sub("}", "\n", response_config)
            response_config = re.sub(":", " =", response_config)
            return "[response]\n\t "+response_config
            
        elif return_format == 'xml':
            ''' Will return in xml format'''
            from core import dicttoobject
            response_xml = xmldict.dict_to_xml(response_dict)
            response_xml = re.sub(">\s*<", ">\n<", response_xml)
            return "\n"+response_xml
        
        elif return_format == 'json':
            ''' Will return in json format'''
            to_do = 'Call dict to xml coverter'
            import json
            response_json = json.dumps(response_dict)
            return response_json
    
    def get_random(self):
        self.random_order = self.random_order + 1
        return self.random_order
        
    def exit(self):
        __builtin__.testthread = None
        sys.exit()

def verifyOptions(options):
    '''
    This will verify the command line options and set to default values, if any option not given in command line.
    '''
    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    #pp.pprint(options)
    verifyTest(options)
    verifyExample(options)
    verifyTestScript(options)
    verifyParams()
    verifyLogdir(options)
    verifyMail(options)
    verifyTestCases(options)

def verifyTest(options):
    if options.testname:
        main.TEST = options.testname
        main.classPath = "tests."+main.TEST+"."+main.TEST
        main.tests_path = tests_path
    elif options.example :
        main.TEST = options.example
        main.tests_path = path+"/examples/"
        main.classPath = "examples."+main.TEST+"."+main.TEST
    else :
        print "Test or Example not specified please specify the --test <test name > or --example <example name>"
        self.exit()

def verifyExample(options):
    if options.example:
        main.testDir = path+'/examples/'
        main.tests_path = path+"/examples/"
        main.classPath = "examples."+main.TEST+"."+main.TEST
               
def verifyLogdir(options):
    #Verifying Log directory option      
    if options.logdir:
        main.logdir = options.logdir
    else :
        main.logdir = main.FALSE  
        
def verifyMail(options):
    # Checking the mailing list 
    if options.mail:
        main.mail = options.mail
    elif main.params.has_key('mail'):
        main.mail = main.params['mail']
    else :
        main.mail = 'paxweb@paxterrasolutions.com'

def verifyTestCases(options):
    #Getting Test cases list 
    if options.testcases:
	testcases_list = options.testcases 
        #sys.exit() 
        testcases_list = re.sub("(\[|\])", "", options.testcases)
        main.testcases_list = eval(testcases_list+",")
    else :
        if 'testcases' in main.params.keys():
            temp = eval(main.params['testcases']+",")
            list1=[]
            if type(temp[0])==list:
	        for test in temp:
      	            for testcase in test:
	                if type(testcase)==int:
		            testcase=[testcase]
	                list1.extend(testcase)
	    else :
	    	temp=list(temp)
      	        for testcase in temp:
	            if type(testcase)==int:
		        testcase=[testcase]
	            list1.extend(testcase)
	    main.testcases_list=list1	                                     
        else :
            print "testcases not specifed in params, please provide in params file or 'testcases' commandline argument"
            sys.exit() 
                  
def verifyTestScript(options):
    '''
    Verifyies test script.
    '''
    main.openspeak = openspeak.OpenSpeak()        
    openspeakfile = main.testDir+"/" + main.TEST + "/" + main.TEST + ".ospk"
    testfile = main.testDir+"/" + main.TEST + "/" + main.TEST + ".py"
    if os.path.exists(openspeakfile) :
        main.openspeak.compiler(openspeakfile=openspeakfile,writetofile=1)
    elif os.path.exists(testfile):
        print ''
    else:
        print "\nThere is no :\""+main.TEST+"\" test, Please Provide OpenSpeak Script/ test script"
        __builtin__.testthread = None
        main.exit()
              
    try :
        testModule = __import__(main.classPath, globals(), locals(), [main.TEST], -1)
    except(ImportError):
        print "There is no test like "+main.TEST
        main.exit()       

    testClass = getattr(testModule, main.TEST)
    main.testObject = testClass()
    load_parser()
    main.params = main.parser.parseParams(main.classPath)    
    main.topology = main.parser.parseTopology(main.classPath) 
    
def verifyParams():
    try :
        main.params = main.params['PARAMS']
    except(KeyError):
        print "Error with the params file: Either the file not specified or the format is not correct"
        main.exit()            
    
    try :
        main.topology = main.topology['TOPOLOGY']
    except(KeyError):
        print "Error with the Topology file: Either the file not specified or the format is not correct"
        main.exit()
        
def load_parser() :
    '''
    It facilitates the loading customised parser for topology and params file.
    It loads parser mentioned in tab named parser of teston.cfg file.
    It also loads default xmlparser if no parser have specified in teston.cfg file.

    '''
    confighash = main.configDict
    if 'file' in confighash['config']['parser'] and 'class' in confighash['config']['parser']:
        if confighash['config']['parser']['file'] != None or confighash['config']['parser']['class']!= None :
            if os.path.exists(confighash['config']['parser']['file']) :
                module = re.sub(r".py\s*$","",confighash['config']['parser']['file'])
                moduleList = module.split("/")
                newModule = ".".join([moduleList[len(moduleList) - 2],moduleList[len(moduleList) - 1]])
                try :
                    parsingClass = confighash['config']['parser']['class']
                    parsingModule = __import__(newModule, globals(), locals(), [parsingClass], -1)
                    parsingClass = getattr(parsingModule, parsingClass)
                    main.parser = parsingClass()
                    #hashobj = main.parser.parseParams(main.classPath)
                    if hasattr(main.parser,"parseParams") and hasattr(main.parser,"parseTopology") and hasattr(main.parser,"parse") :
                        
                        pass
                    else:
                        main.exit()

                except ImportError:
                    print sys.exc_info()[1]
                    main.exit()
            else :
                print "No Such File Exists !!"+ confighash['config']['parser']['file'] +"using default parser"
                load_defaultParser() 
        elif confighash['config']['parser']['file'] == None or confighash['config']['parser']['class'] == None :  
            load_defaultParser() 
    else:
        load_defaultParser()

def load_defaultParser():
    '''
    It will load the default parser which is xml parser to parse the params and topology file.
    '''
    moduleList = main.parserPath.split("/")
    newModule = ".".join([moduleList[len(moduleList) - 2],moduleList[len(moduleList) - 1]])
    try :
        parsingClass = main.parsingClass 
        parsingModule = __import__(newModule, globals(), locals(), [parsingClass], -1)
        parsingClass = getattr(parsingModule, parsingClass)
        main.parser = parsingClass()
        if hasattr(main.parser,"parseParams") and hasattr(main.parser,"parseTopology") and hasattr(main.parser,"parse") :
            pass
        else:
            main.exit()

    except ImportError:
        print sys.exc_info()[1]


def load_logger() :
    '''
    It facilitates the loading customised parser for topology and params file.
    It loads parser mentioned in tab named parser of teston.cfg file.
    It also loads default xmlparser if no parser have specified in teston.cfg file.

    '''
    confighash = main.configDict
    if 'file' in confighash['config']['logger'] and 'class' in confighash['config']['logger']:
        if confighash['config']['logger']['file'] != None or confighash['config']['logger']['class']!= None :
            if os.path.exists(confighash['config']['logger']['file']) :
                module = re.sub(r".py\s*$","",confighash['config']['logger']['file'])
                moduleList = module.split("/")
                newModule = ".".join([moduleList[len(moduleList) - 2],moduleList[len(moduleList) - 1]])
                try :
                    loggerClass = confighash['config']['logger']['class']
                    loggerModule = __import__(newModule, globals(), locals(), [loggerClass], -1)
                    loggerClass = getattr(loggerModule, loggerClass)
                    main.logger = loggerClass()
                    #hashobj = main.parser.parseParams(main.classPath)

                except ImportError:
                    print sys.exc_info()[1]
            else :
                print "No Such File Exists !!"+confighash['config']['logger']['file']+ "Using default logger"
                load_defaultlogger()
        elif confighash['config']['parser']['file'] == None or confighash['config']['parser']['class'] == None :  
            load_defaultlogger() 
    else:
        load_defaultlogger()

def load_defaultlogger():
    '''
    It will load the default parser which is xml parser to parse the params and topology file.
    '''
    moduleList = main.loggerPath.split("/")
    newModule = ".".join([moduleList[len(moduleList) - 2],moduleList[len(moduleList) - 1]])
    try :
        loggerClass = main.loggerClass 
        loggerModule = __import__(newModule, globals(), locals(), [loggerClass], -1)
        loggerClass = getattr(loggerModule, loggerClass)
        main.logger = loggerClass()

    except ImportError:
        print sys.exc_info()[1]
        main.exit()    

def load_defaultlogger():
    '''
    It will load the default parser which is xml parser to parse the params and topology file.
    '''
    moduleList = main.loggerPath.split("/")
    newModule = ".".join([moduleList[len(moduleList) - 2],moduleList[len(moduleList) - 1]])
    try :
        loggerClass = main.loggerClass 
        loggerModule = __import__(newModule, globals(), locals(), [loggerClass], -1)
        loggerClass = getattr(loggerModule, loggerClass)
        main.logger = loggerClass()

    except ImportError:
        print sys.exc_info()[1]
        main.exit()




def _echo(self):
    print "THIS IS ECHO"
