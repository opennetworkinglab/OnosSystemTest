#/usr/bin/env python
'''
Created on 20-Dec-2012

@author: Raghav Kashyap(raghavkashyap@paxterrasolutions.com)


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


'''
import re
import inspect


class OpenSpeak:

    def __init__(self):
        self.default = ''
        self.flag = 0
        self.CurrentStep = 0
        self.grtrOrLssr = 0

    def compiler(self,**compileParameters):
        '''
         This method will parse the openspeak file and will write to a python module with the equivalent translations.
         It can accept OpenSpeak syntax in string or an OpenSpeak file as an input parameter.
         Translated form can be written into python module if attribute "WRITETOFILE" is set to 1.
        '''

        args = self.parse_args(["OPENSPEAKFILE","TEXT","WRITETOFILE","FILEHANDLE"],**compileParameters)
        resultString = ''
        Test = "Mininet"
        args["WRITETOFILE"] = args["WRITETOFILE"] if args["WRITETOFILE"] != None else 1
        self.CurrentStep = 0
        self.CurrentCase = ''

        ## here Open Speak file will be parsed by each line and translated.
        if args["OPENSPEAKFILE"] !=None and args["TEXT"] ==None and args["FILEHANDLE"] == None:
            self.openspeakfile = args["OPENSPEAKFILE"]
            openSpeakFile = open(args["OPENSPEAKFILE"],"r").readlines()

        elif args["OPENSPEAKFILE"] ==None and args["TEXT"] and args["FILEHANDLE"] == None:
            openSpeakFile =  args["TEXT"].split("\n")
        elif args["FILEHANDLE"] and args["OPENSPEAKFILE"] ==None and args["TEXT"] ==None:
            openSpeakFile = args["FILEHANDLE"].readlines()

        index = 0
        outputFile = []
        testName = re.search("\/(.*)\.ospk$",self.openspeakfile,0)
        testName = testName.group(1)
        testName = testName.split("/")
        testName = testName[len(testName)-1]
        outputFile.append("\nclass " + testName + " :" + "\n")
        outputFile.append("\n" + " " * 4 + "def __init__(self) :")
        outputFile.append("\n" + " " * 8 + "self.default = \'\'" + "\n")

        while index < len(openSpeakFile):
            ifelseMatch = re.match("\s+IF|\s+ELSE|\s+ELIF",openSpeakFile[index],flags=0)
            line = openSpeakFile[index]
            repeatMatch = re.match("\s*REPEAT", openSpeakFile[index], flags=0)
            if ifelseMatch :
                result =  self.verify_and_translate(line)
                initialSpaces = len(line) -len(line.lstrip())
                self.outLoopSpace = initialSpaces
                nextLine = openSpeakFile[index+1]
                nextinitialSpaces = len(nextLine) -len(nextLine.lstrip())


                while nextinitialSpaces > initialSpaces :
                    try :
                        elseMatch = re.match("\s*ELSE|\s*ELIF",nextLine,flags=0)
                        if elseMatch :
                            self.flag = self.flag -1
                        result = result + self.verify_and_translate(nextLine)
                        nextLine = openSpeakFile[index + 1]
                        nextinitialSpaces = len(nextLine) -len(nextLine.lstrip())
                    except IndexError:
                        pass
                    index = index + 1
                self.flag = 0
            elif repeatMatch:
                self.flag = 0
                result =  self.verify_and_translate(line)
                index = index + 1
                endMatch = re.match("\s*END",openSpeakFile[index],flags=0)
                while not endMatch :
                    try :

                        self.flag = self.flag + 1
                        result =  result + self.verify_and_translate(openSpeakFile[index])
                        index = index + 1

                    except IndexError :
                        pass


            else :
                self.flag = 0
                result = self.verify_and_translate(line)
                index = index + 1
            outputFile.append(result)

        if args["WRITETOFILE"] == 1 :
            testscript = re.sub("ospk","py",self.openspeakfile,0)
            testScript = open(testscript,"w")
            for lines in outputFile :
                testScript.write(lines)
            testScript.close()
        return resultString

    def verify_and_translate(self,line):
        '''
          It will accept the each line and calls the suitable API to conver into pyton equivalent syntax .
          It will return the translated python syntax .
        '''
        lineSpace = re.match("^\s+",line,flags=0)
        initialSpaces = len(line) -len(line.lstrip())
        line = re.sub("^\s+","",line) if lineSpace else line


        resultString = None
        resultString = "\n" + " " * 4 if str(inspect.stack()[1][3]) == "compiler" else "\n"
        indent = " " *(4 + 4 * self.flag) if self.flag > 0 else " " * 4
        caseMatch = re.search("^CASE\s+(\d+)",line,flags=0)
        nameMatch = re.match("^NAME\s+\"(.*)\"",line,flags=0)
        commentMatch = re.match("^COMMENT\s+\"(.*)\"",line,flags=0)
        stepMatch = re.match("^STEP\s+\"(.*)\"",line,flags=0)
        connectMatch = re.match("^CONNECT\s+(\w+)\s+USING\s+(.*)",line,flags=0)
        disconnectMatch = re.match("^DISCONNECT\s+(.*)",line,flags=0)
        ondoMatch = re.match("^ON\s+(.*)\s+DO\s+(.*)",line,flags=0)

        storeMatch = re.match("^STORE\s+(.*)\s+IN\s+(.*)",line,flags=0)
        variableMatch = re.match("^(.*)\s+=\s+(.*)",line,flags=0)
        assertMatch = re.match("^ASSERT\s+(\w+)\s+(.*)\s+(.*)\s+ONPASS\s+(.*)\s+ONFAIL\s+(.*)",line,flags=0)
        logMatch = re.match("^(ERROR|INFO|DEBUG|CRITICAL|REPORT|EXACT|WARN)\s+(.*)",line,flags=0)
        ifloop = re.match("IF\s+(\w+)\s*(..|\w+)\s*(.*)",line,flags=0)
        elseloopMatch = re.match("ELSE\s*$",line,flags=0)
        elifloop = re.match("ELSE\sIF\s+(\w+)\s*(..|\w+)\s*(.*)",line,flags=0)
        forloopMatch = re.match("\s*REPEAT\s+(/d+)\s+TIMES",line,flags=0)
        experimentalMatch = re.match("EXPERIMENTAL\s+MODE\s+(\w+)",line,flags=0)
        repeatMatch = re.match("\s*REPEAT\s+(\d+)\s+TIMES", line, flags=0)

        response_pasrse = re.match("\s*PARSE\s+(\w+)\s+AS\s+(\w+)\s+INTO\s+(\w+)", line, flags=0)

        if caseMatch :
            self.CurrentStep = 0
            self.CurrentCase = "CASE" + caseMatch.group(1)
            resultString = resultString + self.translate_case_block(casenumber=caseMatch.group(1))
        elif repeatMatch:
            resultString = resultString + indent + self.translate_repeat(repeat=repeatMatch.group(1))
        elif nameMatch :
            resultString = resultString +  indent + self.translate_testcase_name(testname=nameMatch.group(1))
        elif commentMatch :
            resultString = resultString + indent + self.translate_comment(comment=commentMatch.group(1))
        elif stepMatch :
            self.CurrentStep = self.CurrentStep + 1
            resultString = resultString + indent + self.translate_step(step=stepMatch.group(1))
        elif connectMatch :
            resultString = resultString + indent + self.translate_connect(component=connectMatch.group(1),
                                                                           arguments=connectMatch.group(2) )
        elif disconnectMatch :
            resultString = resultString + indent + self.translate_disconnect(component=disconnectMatch.group(1))
        elif ondoMatch :
            resultString = resultString + indent + self.translate_onDOAs(component=ondoMatch.group(1),action=ondoMatch.group(2))
        elif storeMatch :
            resultString = resultString + indent + self.translate_store(variable=storeMatch.group(2),
                                                                         value=storeMatch.group(1))
        elif variableMatch :
            resultString = resultString + indent + self.translate_store(variable=variableMatch.group(1),
                                                                         value=variableMatch.group(2))
        elif assertMatch :
            resultString = resultString + indent + self.translate_assertion(leftvalue=assertMatch.group(1),
                                                                        operator=assertMatch.group(2),
                                                                            rightvalue=assertMatch.group(3),
                                                                            onpass=assertMatch.group(4),
                                                                            onfail=assertMatch.group(5))
        elif logMatch :
            resultString = resultString + indent + self.translate_logs(loglevel=logMatch.group(1),
                                                                        message=logMatch.group(2))
        elif ifloop :

            self.initSpace = initialSpaces
            operand = ifloop.group(1)
            operator = ifloop.group(2)
            value = ifloop.group(3)
            resultString = resultString + indent + "if " + operand + self.translate_if_else_operator(conditionoperator=operator) + value + ":"
            self.flag = self.flag + 1
        elif experimentalMatch :
            resultString = resultString + indent + self.translate_experimental_mode(mode=experimentalMatch.group(1))

        elif elseloopMatch :
            if initialSpaces == self.initSpace or initialSpaces == self.outLoopSpace:
                resultString = resultString + indent + "else :"
                self.flag = self.flag + 1
            else :
                indent = " " *(4 + 4 * (self.flag-1))
                resultString = resultString + indent + "else :"
                self.flag = self.flag + 1

        elif elifloop :

            operand = elifloop.group(1)
            operator = elifloop.group(2)
            value = elifloop.group(3)
            if initialSpaces == self.initSpace or initialSpaces == self.outLoopSpace:
                resultString = resultString + indent + "elif " + operand + self.translate_if_else_operator(conditionoperator=operator) + value + ":"
                self.flag = self.flag + 1
            else :
                indent = " " *(4 + 4 * (self.flag-1))
                resultString = resultString + indent + "elif " + operand + self.translate_if_else_operator(conditionoperator=operator) + value + ":"
                self.flag = self.flag + 1
        elif response_pasrse :
            output_string = response_pasrse.group(1)
            req_format = response_pasrse.group(2)
            store_in = response_pasrse.group(3)
            resultString = resultString + indent + store_in +'= main.response_parser('+output_string+",\""+req_format+"\")"
            self.flag = self.flag + 1

        return resultString

    def translate_repeat(self,**repeatStatement):
        '''
        this will transalte the repeat statement into a python equivalen while loop
        '''

        args = self.parse_args(["REPEAT"],**repeatStatement)
        resultString = ''

        resultString = "i = 0"
        resultString = resultString + "\n" + " " * 8 +"while i<" + args["REPEAT"] + " :"
        return resultString

    def translate_if_else_operator(self,**loopBlock):
        '''
          This method will translate if-else loop block into its equivalent python code.
          Whole loop block will be passed into loopBlock List.
          It returns the transalted reuslt as a string.
        '''
        args = self.parse_args(["CONDITIONOPERATOR"],**loopBlock)
        resultString = ''
        # process the loopBlock List translate all statements underlying the given loop block
        equalsMatch = re.match("EQUALS$|==\s*$",args["CONDITIONOPERATOR"],flags=0)
        greaterMatch = re.match("GREATER\s+THAN$|>\s*$",args["CONDITIONOPERATOR"],flags=0)
        lesserMatch = re.match("LESSER\s+THAN$|<\s*$",args["CONDITIONOPERATOR"],flags=0)
        greaterEqualMatch =  re.match("GREATER\s+THAN\s+OR\s+EQUALS$|>=\s*$",args["CONDITIONOPERATOR"],flags=0)
        lesserEqualMatch = re.match("LESSER\s+THAN\s+OR\s+EQUALS$|<=\s*$",args["CONDITIONOPERATOR"],flags=0)
        if equalsMatch :
            resultString = resultString + " == "
        elif greaterMatch :
            resultString = resultString + " > "
        elif lesserMatch :
            resultString = resultString + " < "
        elif greaterEqualMatch:
            resultString = resultString + " >= "
        elif lesserEqualMatch :
            resultString = resultString + " <= "
        else :
            print "\n Error: Given Operator is not listed "

        return resultString

    def translate_experimental_mode(self,**modeType):
        '''
         This API will translate statment EXPERIMENTAL MODE ON/OFF into python equivalent.
         It will return the transalted value.
         '''
        args = self.parse_args(["MODE"],**modeType)
        resultString = ''
        ONmatch = re.match("\s*ON",args["MODE"],flags=0)
        OFFmatch = re.match("\sOFF",args["MODE"],flags=0)

        if ONmatch :
            resultString = "main.EXPERIMENTAL_MODE = main.TRUE"
        elif OFFmatch :
            resultString = "main.EXPERIMENTAL_MODE = main.FALSE"

        return resultString

    def interpret(self,**interpetParameters):
        '''
         This method will accept the OpenSpeak syntax into a string and will return
         a python equivalent translations statement
        '''

        args = self.parse_args(["TEXT","WRITETOFILE"],**interpetParameters)
        resultString = ''
        ## here Open Speak syntax will be translated into python equivalent.
        resultString = self.verify_and_translate(args["TEXT"])
        lineSpace = re.match("^\s+",resultString,flags=0)

        resultString = re.sub("^\s+","",resultString) if lineSpace else resultString
        return resultString

    def translate_logs(self,**logStatement):
        '''
         This will translate the OpenSpeak log message statements into python equivalent
         to resultString and returns resultString
        '''
        args = self.parse_args(["LOGLEVEL","MESSAGE"],**logStatement)
        resultString = ''
        # convert the statement here
        message = self.translate_log_message(message=args["MESSAGE"])
        if args["LOGLEVEL"] == "INFO" :
            resultString = resultString + "main.log.info(" + message + ")"
        elif args["LOGLEVEL"] == "ERROR" :
            resultString = resultString + "main.log.error(" + message  + ")"
        elif args["LOGLEVEL"] == "DEBUG" :
            resultString = resultString + "main.log.debug(" + message + ")"
        elif args["LOGLEVEL"] == "REPORT" :
            resultString = resultString + "main.log.report(" + message + ")"
        elif args["LOGLEVEL"] == "CRITICAL" :
            resultString = resultString + "main.log.critical(" + message + ")"
        elif args["LOGLEVEL"] == "WARN" :
            resultString = resultString + "main.log.warn(" + args["MESSAGE"] + ")"
        elif args["LOGLEVEL"] == "EXACT" :
            resultString = resultString + "main.log.exact(" + args["MESSAGE"] + ")"


        return resultString

    def translate_log_message(self,**messageStatement) :
        '''
         This API will translate log messages if it is a string or Variable or combination
         of string and variable.
         It will return the analysed and translate message.
        '''
        args = self.parse_args(["MESSAGE"],**messageStatement)
        resultString = ''

        paramsMatch = re.match("PARAMS\[(.*)\]|STEP\[(.*)\]|TOPO\[(.*)\]|CASE\[(.*)\]|LAST_RESULT|LAST_RESPONSE",args["MESSAGE"],flags=0)
        stringMatch = re.match("\s*\"(.*)\"\s*$",args["MESSAGE"],flags=0)
        stringWidVariableMatch = re.match("\"(.*)\"\s+\+\s+(.*)",args["MESSAGE"],flags=0)
        varRefMatch = re.search("\<(\w+)\>",args["MESSAGE"],flags=0)
        if paramsMatch :
            resultString = resultString + self.translate_parameters(parameters=args["MESSAGE"])
        elif stringMatch :
            resultString = resultString + args["MESSAGE"]
        elif stringWidVariableMatch:
            quoteWord = stringWidVariableMatch.group(1)
            variableRef = stringWidVariableMatch.group(2)
            varMatch = re.search("PARAMS\[(.*)\]|STEP\[(.*)\]|TOPO\[(.*)\]|CASE\[(.*)\]",variableRef,flags=0)
            varRefMatch = re.search("\<(\w+)\>",variableRef,flags=0)
            if varMatch :
                resultString = resultString + "\"" + quoteWord + "\"" + " + " + self.translate_parameters(parameters=variableRef)
            elif varRefMatch :
                resultString = resultString + "\"" + quoteWord + "\"" +  " + " + varRefMatch.group(1)
        elif varRefMatch:
            resultString = resultString + varRefMatch.group(1)
        else :
            print "\nError : Syntax error , Not defined way to give log message" + args["MESSAGE"]

        return resultString

    def translate_assertion(self,**assertStatement):
        '''
         This will translate the ASSERT <value1> <COMPARISON OPERATOR> <value2> into python
         equivalent to resultString and returns resultString
        '''
        args = self.parse_args(["LEFTVALUE","OPERATOR","RIGHTVALUE","ONPASS","ONFAIL"],**assertStatement)
        resultString = ''
        # convert the statement here
        notOperatorMatch = re.search("NOT\s+(.*)",args["OPERATOR"],flags=0)
        notOperatorSymbMatch = re.search("\!(.*)",args["OPERATOR"],flags=0)
        operator = ''
        lastresultMatch = re.match("LAST_RESULT",args["RIGHTVALUE"],flags=0)
        lastresponseMatch = re.match("LAST_RESPONSE",args["RIGHTVALUE"],flags=0)
        if lastresultMatch :
            operator = "main.last_result"
        elif lastresponseMatch :
            operator = "main.last_response"
        else :
            operator = args["RIGHTVALUE"]

        if args["OPERATOR"] == None or args["OPERATOR"] == "" :
            print "\n Error : Operator has not been specified !!!"
        elif notOperatorMatch or notOperatorSymbMatch:

            operators = notOperatorMatch.group(1) if notOperatorMatch else notOperatorSymbMatch.group(1)
            operators = self.translate_operator(operator=operators)
            if self.grtrOrLssr == 0 :
                resultString = resultString + "utilities.assert_not_" + operators + "(expect=" +\
                               self.translate_response_result(operator=args["RIGHTVALUE"]) + ",actual=" + self.translate_response_result(operator=args["LEFTVALUE"]) +\
                               ",onpass=" + self.translate_assertMessage(message=args["ONPASS"]) +\
                               ",onfail=" + self.translate_assertMessage(message=args["ONFAIL"]) + ")"
            else :
                resultString = resultString + "utilities.assert_not_" + operators + "(expect=" +\
                               self.translate_response_result(operator=args["LEFTVALUE"]) + ",actual=" + self.translate_response_result(operator=args["RIGHTVALUE"]) +\
                               ",onpass=" + self.translate_assertMessage(message=args["ONPASS"]) +\
                               ",onfail=" + self.translate_assertMessage(message=args["ONFAIL"]) + ")"

        else :
            operators = self.translate_operator(operator=args["OPERATOR"])
            if self.grtrOrLssr == 0 :
                resultString = resultString + "utilities.assert_" + operators + "(expect=" +\
                               self.translate_response_result(operator=args["RIGHTVALUE"]) +\
                               ",actual=" + self.translate_response_result(operator=args["LEFTVALUE"]) +\
                               ",onpass=" + self.translate_assertMessage(message=args["ONPASS"]) +\
                               ",onfail=" + self.translate_assertMessage(message=args["ONFAIL"]) + ")"
            else :
                resultString = resultString + "utilities.assert_" + operators + "(expect=" +\
                               self.translate_response_result(operator=args["LEFTVALUE"]) +\
                               ",actual=" + self.translate_response_result(operator=args["RIGHTVALUE"]) +\
                               ",onpass=" + self.translate_assertMessage(message=args["ONPASS"]) +\
                               ",onfail=" + self.translate_assertMessage(message=args["ONFAIL"]) + ")"


        return resultString

    def translate_response_result(self,**operatorStatement):
        '''
         It will translate the LAST_RESPONSE or LAST_RESULT statement into its equivalent.
         It returns the translate form in resulString.
        '''
        args = self.parse_args(["OPERATOR"],**operatorStatement)
        resultString = ''
        lastResultMatch = re.match("LAST_RESULT",args["OPERATOR"],flags=0)
        lastResponseMatch = re.match("LAST_RESPONSE",args["OPERATOR"],flags=0)
        if lastResultMatch :
            resultString = resultString + "main.last_result"
        elif lastResponseMatch:
            resultString = resultString + "main.last_response"
        else :
            resultString = resultString + args["OPERATOR"]
        return resultString


    def translate_assertMessage(self,**messageStatement) :
        '''
         This API will facilitate the translation of assert ONPASS or ONFAIL messages . The message can be
         a string or calling another API in OpenSpeak syntax.
         It will return the translated message
        '''
        args = self.parse_args(["MESSAGE"],**messageStatement)

        connectMatch = re.search("CONNECT\s+(\w+)\s+USING\s+(.*)",args["MESSAGE"],flags=0)
        disconnectMatch = re.search("DISCONNECT\s+(.*)",args["MESSAGE"],flags=0)
        ondoMatch = re.search("ON\s+(.*)\s+DO\s+(.*)",args["MESSAGE"],flags=0)
        paramsMatch = re.search("PARAMS\[(.*)\]|STEP\[(.*)\]|TOPO\[(.*)\]|CASE\[(.*)\]",args["MESSAGE"],flags=0)
        stringMatch = re.search("\"(.*)\"|\'(.*)\'",args["MESSAGE"],flags=0)
        variableMatch = re.search("\<(.*)\>",args["MESSAGE"],flags=0)

        resultString = ''
        if connectMatch :
            resultString = resultString + self.translate_connect(component=connectMatch.group(1),
                                                                 arguments=connectMatch.group(2) )
        elif disconnectMatch :
            resultString = resultString + self.translate_disconnect(component=disconnectMatch.group(1))
        elif ondoMatch :
            resultString = resultString + self.translate_onDOAs(component=ondoMatch.group(1),
                                                                action=ondoMatch.group(2))
        elif paramsMatch :
            resultString = resultString + self.translate_parameters(parameters=args["MESSAGE"])
        elif stringMatch :
            resultString = resultString + "\"" + stringMatch.group(1) + "\""
        elif variableMatch :
            resultString = resultString + variableMatch.group(1)
        elif args["MESSAGE"]  == None :
            print "\n Error : Please pass a message or action for assertion "

        return resultString

    def translate_operator(self,**operatorStatement) :
        '''
          It will translate the operator for assertion , by ensuring against given arguments.
          It will return the translated assertion operator.
        '''
        args = self.parse_args(["OPERATOR"],**operatorStatement)

        resultString = ''
        equalsMatch = re.match("EQUALS$|==$",args["OPERATOR"],flags=0)
        greaterMatch = re.match("GREATER\s+THAN$|>$",args["OPERATOR"],flags=0)
        lesserMatch = re.match("LESSER\s+THAN$|<$",args["OPERATOR"],flags=0)
        stringMatch = re.match("MATCHES|~$",args["OPERATOR"],flags=0)
        greaterEqualMatch =  re.match("GREATER\s+THAN\s+OR\s+EQUALS$|>=$",args["OPERATOR"],flags=0)
        lesserEqualMatch = re.match("LESSER\s+THAN\s+OR\s+EQUALS$|<=$",args["OPERATOR"],flags=0)
        if equalsMatch :

            resultString = resultString + "equals"
        elif greaterMatch :
            self.grtrOrLssr = self.grtrOrLssr + 1
            resultString = resultString + "greater"
        elif lesserMatch :
            self.grtrOrLssr = self.grtrOrLssr + 1
            resultString = resultString + "lesser"
        elif stringMatch :

            resultString = resultString + "matches"
        elif greaterEqualMatch:

            resultString = resultString + "greater_equals"
        elif lesserEqualMatch :

            resultString = resultString + "lesser_equals"
        else :
            print "\n Error: Given Operator is not listed for assertion"
        return resultString

    def translate_store(self,**storeStatement):
        '''
         This will translate the STORE <variable> IN <value> or <variable> = <value>
         into python equivalent to resultString and returns resultString
        '''
        args = self.parse_args(["VARIABLE","VALUE"],**storeStatement)
        resultString = ''
        # convert the statement here
        ondoMatch = re.match("^\s*ON\s+(.*)\s+DO\s+(.*)",args["VALUE"],flags=0)
        paramsMatch = re.match("^\s*PARAMS\[(.*)\]|STEP\[(.*)\]|TOPO\[(.*)\]|CASE\[(.*)\]|LAST_RESULT|LAST_RESPONSE",args["VALUE"],flags=0)
        if paramsMatch :
            argString = self.translate_parameters(parameters=args["VALUE"])
            resultString = args["VARIABLE"] + " = " + argString
        elif ondoMatch :
            resultString = args["VARIABLE"] + " = "  + self.translate_onDOAs(component=ondoMatch.group(1),action=ondoMatch.group(2))
        else :
            resultString = args["VARIABLE"] + " = " + args["VALUE"]


        return resultString

    def translate_disconnect(self,**disconnectStatement):
        '''
         This will translate the DISCONNECT <component_name> into python
         equivalent to resultString and returns resultString
        '''
        args = self.parse_args(["COMPONENT"],**disconnectStatement)
        resultString = ''
        # convert the statement here
        resultString = "main." + args["COMPONENT"] + ".disconnect()"
        return resultString

    def translate_onDOAs(self,**onDoStatement):
        '''
         This will translate the ON <component> DO <action> USING <arg1> AS <value1>,<arg2> AS <value2>
         into python equivalent to resultString and returns resultString
        '''
        args = self.parse_args(["COMPONENT","ACTION","ARGUMENTS"],**onDoStatement)
        subString = ''

        usingMatch = re.match("\s*(.*)\s+USING\s+(.*)",args["ACTION"],flags=0)
        action = ''
        if usingMatch :
            action = usingMatch.group(1)
            arguments = usingMatch.group(2)
            subString = self.translate_usingas(arguments=arguments)

        else :
            andCheck = re.search ("(.*)\s+AND\s+(.*)",args["ACTION"],flags=0)

            action = action + "()"
            if andCheck:
                action = andCheck.group(1) + "()"
                subString = subString + self.handle_conjuction(statement=andCheck.group(2))
            else :
                action = args["ACTION"]
                action = action + "()"
        # convert the statement here
        resultString = "main." + args["COMPONENT"] + "." + action + subString
        return resultString


    def handle_conjuction(self,**conjuctStatement):
        '''
        This will handle the conjuctions
        '''

        args = self.parse_args(["STATEMENT"],**conjuctStatement)
        subSentence = ''

        storeMatch = re.match("\s*STORE\s+(.*)\s+IN\s+(.*)",args["STATEMENT"],flags=0)
        assertMatch = re.match("\s*ASSERT\s+(\w+)\s+(.*)\s+(.*)\s+ONPASS\s+(.*)\s+ONFAIL\s+(.*)",args["STATEMENT"],flags=0)
        if storeMatch :
            subSentence =  "\n" + " " * 8 + self.translate_store(variable=storeMatch.group(2),
                                                                         value=storeMatch.group(1))
        elif assertMatch :
            subSentence = "\n" + " " * 8 + self.translate_assertion(leftvalue=assertMatch.group(1),
                                                                    operator=assertMatch.group(2),
                                                                    rightvalue=assertMatch.group(3),
                                                                    onpass=assertMatch.group(4),
                                                                    onfail=assertMatch.group(5))
        return subSentence

    def translate_usingas(self,**argumentAS) :
        '''
         This will tranlate USING argument AS value Statement into equivalent argument passing.
         It will return translated form into resultString
        '''
        args = self.parse_args(["ARGUMENTS"],**argumentAS)
        resultString = ''
        argsList = []
        subString = ''
        subSentence = ''
        line = ''
        andCheck = re.search ("(.*)\s+AND\s+(.*)",args["ARGUMENTS"],flags=0)
        if andCheck:
            line = andCheck.group(1)
            subSentence = self.handle_conjuction(statement=andCheck.group(2))
        else :
            line = args["ARGUMENTS"]



        argsMatch = re.search("(.*),(.*)",line,flags=0)


        if args["ARGUMENTS"] == None or args["ARGUMENTS"] == '' :
            subString = ''
        elif argsMatch :

            argsList = line.split(",")
            for index, arguments in enumerate(argsList):
                argMatch = re.search("(.*)\s+AS\s+(.*)",arguments,flags=0)
                if argMatch:
                    argsKey =  argMatch.group(1)
                    argsValue = argMatch.group(2)
                    paramsMatch = re.search("PARAMS\[(.*)\]|STEP\[(.*)\]|TOPO\[(.*)\]|CASE\[(.*)\]|LAST_RESPONSE|LAST_RESULT",argsValue,flags=0)
                    if not paramsMatch :
                        if index == len(argsList) - 1 :
                            subString = subString +  argsKey + "=" + argsValue
                        else :
                            subString = subString +  argsKey + "=" + argsValue + ","
                    else :
                        argString = self.translate_parameters(parameters=argsValue)
                        if index == len(argsList) - 1 :
                            subString = subString +  argsKey + "=" + argString
                        else :
                            subString = subString +  argsKey + "=" + argString + ","
                else :
                    if index == len(argsList) - 1 :
                        subString = subString +  arguments
                    else :
                        subString = subString + arguments + ","
        else :
            argMatch = re.search("(.*)\s+AS\s+(.*)",args["ARGUMENTS"],flags=0)
            if argMatch:
                argsKey =  argMatch.group(1)
                argsValue = argMatch.group(2)
                paramsMatch = re.search("PARAMS\[(.*)\]|STEP\[(.*)\]|TOPO\[(.*)\]|CASE\[(.*)\]|LAST_RESPONSE|LAST_RESULT",argsValue,flags=0)
                if not paramsMatch :
                    subString = subString +  argsKey + "=" + argsValue
                else :
                    argString = self.translate_parameters(parameters=argsValue)
                    subString = subString +  argsKey + "=" + argString
            else :
                paramsMatch = re.match("PARAMS\[(.*)\]|STEP\[(.*)\]|TOPO\[(.*)\]|CASE\[(.*)\]|LAST_RESPONSE|LAST_RESULT",line,flags=0)
                if paramsMatch :
                    subString = subString + self.translate_parameters(parameters=line)
                else :
                    subString = subString +  line
        resultString = "(" + subString + ")"+ subSentence
        return resultString


    def translate_connect(self,**connectStatement):
        '''
         This will translate the CONNECT <component_name> USING1 <arg1> AS <value1>, <arg2> AS <value2>
         into python equivalent to resultString and returns resultString
        '''
        args = self.parse_args(["COMPONENT","ARGUMENTS"],**connectStatement)
        resultString = ''
        subString = self.translate_usingas(arguments=args["ARGUMENTS"])
        # convert the statement here
        resultString = "main." + args["COMPONENT"] + ".connect(" + subString + ")"
        return resultString


    def translate_parameters(self,**parameterStatement):
        '''
         This will translate the OpenSpeak Case and Params parameters into python equivalent
         to resultString and returns resultString
        '''
        args = self.parse_args(["PARAMETERS"],**parameterStatement)
        argument = args["PARAMETERS"]
        resultString = ''
        ### match arguments
        paramsMatch = re.search("PARAMS((\[(.*)\])*)",argument,flags=0)
        stepsMatch = re.search("STEP((\[(.*)\])*)",argument,flags=0)
        casesMatch = re.search("CASE((\[(.*)\])*)",argument,flags=0)
        topoMatch = re.search("TOPO((\[(.*)\])*)",argument,flags=0)
        lastResultMatch = re.match("LAST_RESULT",argument,flags=0)
        lastResponseMatch = re.match("LAST_RESPONSE",argument,flags=0)
        # convert the statement here
        if paramsMatch :
            params = paramsMatch.group(1)
            resultString = resultString + "main.params" + self._argsCheck(checkvar=params)
        elif stepsMatch :
            resultString = resultString +"main.params[\'" + self.CurrentCase +\
                           "\'][\'STEP" + str(self.CurrentStep) + "\']" +\
                           self._argsCheck(checkvar=stepsMatch.group(1))
        elif casesMatch :
            resultString = resultString + "main.params[\'" + self.CurrentCase + "\']" +\
                           self._argsCheck(checkvar=casesMatch.group(1))
        elif topoMatch :
            resultString = resultString + "main.componentDictionary" +\
                           self._argsCheck(checkvar=topoMatch.group(1))
        elif lastResultMatch :
            resultString = resultString + "main.last_result"
        elif lastResponseMatch :
            resultString = resultString + "main.last_response"
        return resultString

    def _argsCheck(self,**args):
        ''' This API will check if given argument is varibale reference or String and will translate accordingly.
            It will return the tanslate form in resultString.
         '''
        args = self.parse_args(["CHECKVAR"],**args)
        params = args["CHECKVAR"]
        argsList = params.split("]")
        resultString = ''
        del argsList[len(argsList) - 1]
        for index,paramArgs in enumerate(argsList) :
            argsWidVariable = re.search("(\"|\')\s*(\w+)\s*(\'|\")",paramArgs,flags=0)
            if argsWidVariable :
                resultString = resultString + "[\'" + argsWidVariable.group(2) + "\']"
            else :
                resultString = resultString + paramArgs + "]"
        return resultString

    def translate_step(self,**stepStatement):
        '''
         This will translate the STEP "DO SOMETHING HERE" into python equivalent
         to resultString and returns resultString
        '''
        args = self.parse_args(["STEP"],**stepStatement)
        resultString = ''
        resultString = "main.step(\"" + args["STEP"] + "\")"
        # convert the statement here
        return resultString


    def translate_comment(self,**commentStatement):
        '''
         This will translate the COMMENT "DO SOMETHING HERE" into python equivalent
         to resultString and returns resultString
        '''
        args = self.parse_args(["COMMENT"],**commentStatement)
        resultString = ''
        resultString = "#" + args["COMMENT"]
        # convert the statement here
        return resultString

    def translate_testcase_name(self,**nameStatement):
        '''
         This method will convert NAME "<Testcase_name>" into python equivalent statement
         to resultString and returns resultString
        '''
        args = self.parse_args(["TESTNAME"],**nameStatement)

        resultString = ''
        resultString = "main.case(\"" + args["TESTNAME"]  + "\")"
        # convert the statement here
        return resultString


    def translate_case_block(self,**caseBlock):
        '''
         This method will translate the case block in test script .
         It returns the translated equivalent python code for test script
        '''
        args = self.parse_args(["CASENUMBER"],**caseBlock)
        resultString = ""
        resultString = "def CASE" + str(args["CASENUMBER"]) + "(self,main) :\n"
        # process the caseBlock List translate all statements underlying the given case
        return resultString



    def translate_loop_block(self,*loopBlock):
        '''
         This method will translate for loop block into its equivalent python code.
         Whole loop block will be passed into loopBlock List.
         It returns the transalted reuslt as a string.
        '''
        resultString = ''
        # process the loopBlock List translate all statements underlying the given loop block
        return resultString


    def translate_conjuction(self,conjuctionStatement):
        '''
         This will translate the AND conjuction statements into python equivalent
         to resultString and returns resultString
        '''
        resultString = ''
        # convert the statement here
        return resultString


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
