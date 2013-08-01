#!/usr/bin/env python
'''
Created on 23-Oct-2012
    
@authors: Anil Kumar (anilkumar.s@paxterrasolutions.com),
          Raghav Kashyap(raghavkashyap@paxterrasolutions.com)



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

        
Utilities will take care about the basic functions like :
   * Extended assertion,
   * parse_args for key-value pair handling
   * Parsing the params or topology file.

'''
import re
from configobj import ConfigObj
import pydoc
from core import ast as ast
import smtplib

import mimetypes
import email
import os
import email.mime.application

class Utilities:
    '''
       Utilities will take care about the basic functions like :
       * Extended assertion,
       * parse_args for key-value pair handling
       * Parsing the params or topology file.
    '''
    
    def __init__(self):
        self.wrapped = sys.modules[__name__]

    def __getattr__(self, name):
        '''
        This will invoke, if the attribute wasn't found the usual ways.
        Here it will look for assert_attribute and will execute when AttributeError occurs.
        It will return the result of the assert_attribute.
        '''
        try:
            return getattr(self.wrapped, name)
        except AttributeError:
            def assertHandling(**kwargs):
                nameVar = re.match("^assert",name,flags=0) 
                matchVar = re.match("assert(_not_|_)(equals|matches|greater|lesser)",name,flags=0)
                notVar = 0
                operators = ""

                try :
                    if matchVar.group(1) == "_not_" and matchVar.group(2) :
                        notVar = 1
                        operators = matchVar.group(2)
                    elif matchVar.group(1) == "_" and matchVar.group(2):
                        operators = matchVar.group(2)
                        
                except AttributeError:
                    if matchVar==None and nameVar:
                        operators ='equals'
                        
                result = self._assert(NOT=notVar,operator=operators,**kwargs) 
                if result == main.TRUE:
                    main.log.info("Assertion Passed")
                    main.CASERESULT = main.TRUE
                elif result == main.FALSE:
                    main.log.warn("Assertion Failed")
                    main.CASERESULT = main.FALSE
                    
                else :
                    main.log.error("There is an Error in Assertion")
                    main.CASERESULT = main.ERROR
                    
                return result
            
            return assertHandling
        
    
    def _assert (self,**assertParam):  
        '''
        It will take the arguments :
        expect:'Expected output' 
        actual:'Actual output' 
        onpass:'Action or string to be triggered or displayed respectively when the assert passed'
        onfail:'Action or string to be triggered or displayed respectively when the assert failed'
        not:'optional argument to specify the negation of the each assertion type'
        operator:'assertion type will be defined by using operator. Like equal , greater, lesser, matches.'
        
        It will return the assertion result.
                
        '''
              
        arguments = self.parse_args(["EXPECT","ACTUAL","ONPASS","ONFAIL","NOT","OPERATOR"],**assertParam)
        
        result = 0
        valuetype = ''
        operation = "not "+ str(arguments["OPERATOR"]) if arguments['NOT'] and arguments['NOT'] == 1 else arguments["OPERATOR"]
        operators = {'equals':{'STR':'==','NUM':'=='}, 'matches' : '=~', 'greater':'>' ,'lesser':'<'}
           
        expectMatch = re.match('^\s*[+-]?0(e0)?\s*$', str(arguments["EXPECT"]), re.I+re.M)
        if not ((not expectMatch) and (arguments["EXPECT"]==0)):
            valuetype = 'NUM'
        else :
            if arguments["OPERATOR"] == 'greater' or arguments["OPERATOR"] == 'lesser':
                main.log.error("Numeric comparison on strings is not possibele")
                return main.ERROR
            
        valuetype = 'STR'
        arguments["ACTUAL"] = str(arguments["ACTUAL"])
        if arguments["OPERATOR"] != 'matches':
            arguments["EXPECT"] = str(arguments["EXPECT"])
 
        try :
            opcode = operators[str(arguments["OPERATOR"])][valuetype] if arguments["OPERATOR"] == 'equals' else operators[str(arguments["OPERATOR"])]
            
        except KeyError:
            print "Key Error in assertion"
            return main.FALSE
        
        if opcode == '=~':
            try:
                assert re.search(str(arguments["EXPECT"]),str(arguments["ACTUAL"]))
                result = main.TRUE
            except AssertionError:
                try :
                    assert re.match(str(arguments["EXPECT"]),str(arguments["ACTUAL"])) 
                    result = main.TRUE
                except AssertionError:
                    main.log.error("Assertion Failed")
                    result = main.FALSE
                    
        else :
            try:
                if str(opcode)=="==":
                    main.log.info("Verifying the Expected is equal to the actual or not using assert_equal")
                    if (arguments["EXPECT"] == arguments["ACTUAL"]):
                        result = main.TRUE
                    else :
                        result = main.FALSE
                        
                elif str(opcode) == ">":
                    main.log.info("Verifying the Expected is Greater than the actual or not using assert_greater")
                    if (ast.literal_eval(arguments["EXPECT"]) > ast.literal_eval(arguments["ACTUAL"])) :
                        result = main.TRUE
                    else :
                        result = main.FALSE
                        
                elif str(opcode) == "<":
                    main.log.info("Verifying the Expected is Lesser than the actual or not using assert_lesser")
                    if (ast.literal_eval(arguments["EXPECT"]) < ast.literal_eval(arguments["ACTUAL"])):
                        result = main.TRUE
                    else :
                        result = main.FALSE
                    
                    
            except AssertionError:
                main.log.error("Assertion Failed")
                result = main.FALSE
                
        
        result = result if result else 0
        result = not result if arguments["NOT"] and arguments["NOT"] == 1 else result
        resultString = ""
        if result :
            resultString = str(resultString) + "PASS"
            main.log.info(arguments["ONPASS"])
        else :
            resultString = str(resultString) + "FAIL"
            if not isinstance(arguments["ONFAIL"],str):
                eval(str(arguments["ONFAIL"]))
            else :
                main.log.error(arguments["ONFAIL"])
                main.log.report(arguments["ONFAIL"])
             
        msg = arguments["ON" + str(resultString)]

        if not isinstance(msg,str):
            try:
                eval(str(msg))
            except SyntaxError:
                print "functin definition is not write"

        main.last_result = result
        return result
    
    
    def parse_args(self,args, **kwargs):
        '''
        It will accept the (key,value) pair and will return the (key,value) pairs with keys in uppercase.
        '''
        newArgs = {}
        for key,value in kwargs.iteritems():
            #currentKey =  str.upper(key)
            if isinstance(args,list) and str.upper(key) in args:
                for each in args:                    
                    if each==str.upper(key):
                        newArgs [str(each)] = value
                    elif each != str.upper(key) and (newArgs.has_key(str(each)) == False ):
                        newArgs[str(each)] = None
                    
                    
            
        return newArgs
    
    def send_mail(self):
        # Create a text/plain message
        msg = email.mime.Multipart.MIMEMultipart()
        try :
            if main.test_target:
                sub = "Result summary of \""+main.TEST+"\" run on component \""+main.test_target+"\" Version \""+vars(main)[main.test_target].get_version()+"\": "+str(main.TOTAL_TC_SUCCESS)+"% Passed"
            else :
                sub = "Result summary of \""+main.TEST+"\": "+str(main.TOTAL_TC_SUCCESS)+"% Passed"
        except KeyError,AttributeError:
            sub = "Result summary of \""+main.TEST+"\": "+str(main.TOTAL_TC_SUCCESS)+"% Passed"
            
        msg['Subject'] = sub
        msg['From'] = 'paxweb@paxterrasolutions.com'
        msg['To'] = main.mail
        #msg['Cc'] = 'paxweb@paxterrasolutions.com'
        
        # The main body is just another attachment
        body = email.mime.Text.MIMEText(main.logHeader+"\n"+main.testResult)
        msg.attach(body)
        
        # Attachment
        for filename in os.listdir(main.logdir):
            filepath = main.logdir+"/"+filename
            fp=open(filepath,'rb')
            att = email.mime.application.MIMEApplication(fp.read(),_subtype="")
            fp.close()
            att.add_header('Content-Disposition','attachment',filename=filename)
            msg.attach(att)
        
        smtp = smtplib.SMTP('198.57.211.46')
        smtp.starttls()
        smtp.login('paxweb@paxterrasolutions.com','pax@peace')
        smtp.sendmail(msg['From'],[msg['To']], msg.as_string())
        smtp.quit()
        return main.TRUE        
        
           
    def parse(self,fileName):
        '''
        This will parse the params or topo or cfg file and return content in the file as Dictionary
        '''
        self.fileName = fileName
        matchFileName = re.match(r'(.*)\.(cfg|params|topo)',self.fileName,re.M|re.I)    
        if matchFileName:
            try :
                parsedInfo = ConfigObj(self.fileName)
                return parsedInfo
            except :
                print "There is no such file to parse "+fileName 
        else:
            return 0   


if __name__ != "__main__":
    import sys
    
    sys.modules[__name__] = Utilities()    
