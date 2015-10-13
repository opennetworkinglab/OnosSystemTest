#/usr/bin/env python
'''
Created on 07-Jan-2013

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

import logging
import datetime
import re
import os
class Logger:
    '''
        Add continuous logs and reports of the test.

        @author: Raghav Kashyap(raghavkashyap@paxterrasolutions.com)
    '''
    def _printHeader(self,main) :
        '''
            Log's header will be append to the Log file
        '''
        logmsg = "\n"+" " * 32+"+----------------+\n" +"-" * 30+" { Script And Files }  "+"-" * 30+"\n" +" " * 32+"+----------------+\n";
        logmsg = logmsg + "\n\tScript Log File : " + main.LogFileName + ""
        logmsg = logmsg + "\n\tReport Log File : " + main.ReportFileName + ""
        for component in main.componentDictionary.keys():
            logmsg = logmsg + "\n\t"+component+" Session Log : " + main.logdir+"/"+component+".session" + ""

        logmsg = logmsg + "\n\tTest Script :" + path + "Tests/" + main.TEST + ".py"+ ""
        logmsg = logmsg + "\n\tTest Params : " + path + "Tests/" + main.TEST + ".params" + ""
        logmsg = logmsg + "\n\tTopology : " + path + "Tests/" +main.TEST + ".topo" + ""
        logmsg = logmsg + "\n"+" " * 30+"+" +"-" * 18+"+" +"\n" +"-" * 27+"  { Script Exec Params }  "+"-" * 27 +"\n" +" " * 30 +"+"+"-" * 18 +"+\n";
        values = "\n\t" + str(main.params)
        values = re.sub(",", "\n\t", values)
        values = re.sub("{", "\n\t", values)
        values = re.sub("}", "\n\t", values)
        logmsg = logmsg + values
        logmsg = logmsg + "\n\n"+" " * 31+"+---------------+\n" +"-" * 29+" { Components Used }  " +"-" * 29+"\n"+" " * 31+"+---------------+\n"
        component_list = []
        component_list.append(None)

        # Listing the components in the order of test_target component should be first.
        if type(main.componentDictionary) == dict:
            for key in main.componentDictionary.keys():
                if main.test_target == key :
                    component_list[0] = key+"-Test Target"
                else :
                    component_list.append(key)

        for index in range(len(component_list)) :
            if index==0:
                if component_list[index]:
                    logmsg+="\t"+component_list[index]+"\n"
            elif index > 0 :
                logmsg+="\t"+str(component_list[index])+"\n"

        logmsg = logmsg + "\n\n"+" " * 30+"+--------+\n" +"-" * 28+" { Topology }  "+"-" * 28 +"\n" +" " * 30+"+--------+\n"
        values = "\n\t" + str(main.topology['COMPONENT'])
        values = re.sub(",", "\n\t", values)
        values = re.sub("{", "\n\t", values)
        values = re.sub("}", "\n\t", values)
        logmsg = logmsg + values
        logmsg = logmsg + "\n"+"-" * 60+"\n"

        # enter into log file all headers
        logfile = open(main.LogFileName,"w+")
        logfile.write (logmsg)
        print logmsg
        main.logHeader = logmsg
        logfile.close()

        #enter into report file all headers
        main.reportFile = open(main.ReportFileName,"w+")
        main.reportFile.write(logmsg)
        main.reportFile.close()

        #Sumamry file header
        currentTime = str( main.STARTTIME.strftime("%d %b %Y %H:%M:%S") )
        main.summaryFile = open( main.SummaryFileName, "w+" )
        main.summaryFile.write( main.TEST + " at " + currentTime + "\n" )
        main.summaryFile.close()

        #wiki file header
        currentTime = str( main.STARTTIME.strftime("%d %b %Y %H:%M:%S") )
        main.wikiFile = open( main.WikiFileName, "w+" )
        main.wikiFile.write( main.TEST + " at " + currentTime + "<p></p>\n" )
        main.wikiFile.close()

    def initlog(self,main):
        '''
            Initialise all the log handles.
        '''
        main._getTest()
        main.STARTTIME = datetime.datetime.now()

        currentTime = re.sub("-|\s|:|\.", "_", str(main.STARTTIME.strftime("%d %b %Y %H:%M:%S")))
        if main.logdir:
            main.logdir = main.logdir+ "/"+main.TEST + "_" + currentTime
        else:
            main.logdir = main.logs_path + main.TEST + "_" + currentTime

        os.mkdir(main.logdir)

        main.LogFileName = main.logdir + "/" + main.TEST + "_" +str(currentTime) + ".log"
        main.ReportFileName = main.logdir + "/" + main.TEST + "_" + str(currentTime) + ".rpt"
        main.WikiFileName = main.logdir + "/" + main.TEST + "Wiki.txt"
        main.SummaryFileName = main.logdir + "/" + main.TEST + "Summary.txt"
        main.JenkinsCSV = main.logdir + "/" + main.TEST + ".csv"
        main.TOTAL_TC_SUCCESS = 0

        #### Add log-level - Report
        logging.addLevelName(9, "REPORT")
        logging.addLevelName(7, "EXACT")
        logging.addLevelName(11, "CASE")
        logging.addLevelName(12, "STEP")
        main.log = logging.getLogger(main.TEST)
        def report(msg):
            '''
                Will append the report message to the logs.
            '''
            main.log._log(9,msg,"OpenFlowAutoMattion","OFAutoMation")
            currentTime = datetime.datetime.now()
            currentTime = currentTime.strftime("%d %b %Y %H:%M:%S")
            newmsg = "\n[REPORT] " +"["+ str(currentTime)+"] "+msg
            print newmsg
            main.reportFile = open(main.ReportFileName,"a+")
            main.reportFile.write(newmsg)
            main.reportFile.close()

        main.log.report = report

        def summary( msg ):
            '''
                Will append the message to the txt file for the summary.
            '''
            main.log._log(6,msg,"OpenFlowAutoMattion","OFAutoMation")
            main.summaryFile = open(main.SummaryFileName,"a+")
            main.summaryFile.write(msg+"\n")
            main.summaryFile.close()

        main.log.summary = summary

        def wiki( msg ):
            '''
                Will append the message to the txt file for the wiki.
            '''
            main.log._log(6,msg,"OpenFlowAutoMattion","OFAutoMation")
            main.wikiFile = open(main.WikiFileName,"a+")
            main.wikiFile.write(msg+"\n")
            main.wikiFile.close()

        main.log.wiki = wiki

        def exact(exmsg):
            '''
               Will append the raw formatted message to the logs
            '''
            main.log._log(7,exmsg,"OpenFlowAutoMattion","OFAutoMation")
            main.reportFile = open(main.ReportFileName,"a+")
            main.reportFile.write(exmsg)
            main.reportFile.close()
            logfile = open(main.LogFileName,"a")
            logfile.write("\n"+ str(exmsg) +"\n")
            logfile.close()
            print exmsg

        main.log.exact = exact

        def case(msg):
            '''
               Format of the case type log defined here.
            '''
            main.log._log(9,msg,"OpenFlowAutoMattion","OFAutoMation")
            currentTime = datetime.datetime.now()
            newmsg = "["+str(currentTime)+"] " + "["+main.TEST+"] " + "[CASE] " +msg
            logfile = open(main.LogFileName,"a")
            logfile.write("\n"+ str(newmsg) +"\n")
            logfile.close()
            print newmsg

        main.log.case = case

        def step(msg):
            '''
                Format of the step type log defined here.
            '''
            main.log._log(9,msg,"OpenFlowAutoMattion","OFAutoMation")
            currentTime = datetime.datetime.now()
            newmsg = "["+str(currentTime)+"] " + "["+main.TEST+"] " + "[STEP] " +msg
            logfile = open(main.LogFileName,"a")
            logfile.write("\n"+ str(newmsg) +"\n")
            logfile.close()
            print newmsg

        main.log.step = step

        main.LogFileHandler = logging.FileHandler(main.LogFileName)
        self._printHeader(main)

        ### initializing logging module and settig log level
        main.log.setLevel(logging.INFO)
        main.log.setLevel(logging.DEBUG) # Temporary
        main.LogFileHandler.setLevel(logging.INFO)

        # create console handler with a higher log level
        main.ConsoleHandler = logging.StreamHandler()
        main.ConsoleHandler.setLevel(logging.INFO)
        main.ConsoleHandler.setLevel(logging.DEBUG) #Temporary
        # create formatter and add it to the handlers
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        class MyFormatter( logging.Formatter ):
            colors = { 'cyan': '\033[96m', 'purple': '\033[95m',
                       'blue': '\033[94m', 'green': '\033[92m',
                       'yellow': '\033[93m', 'red': '\033[91m',
                       'end': '\033[0m' }

            FORMATS = {'DEFAULT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'}
            if COLORS:  # NOTE:colors will only be loaded if command is run from one line
                        #      IE:   './cli.py run testname'
                        #      This is to prevent issues with Jenkins parsing
                        # TODO: Make colors configurable
                levels = { logging.ERROR : colors['red'] +
                                           FORMATS['DEFAULT'] +
                                           colors['end'],
                           logging.WARN : colors['yellow'] +
                                          FORMATS['DEFAULT'] +
                                          colors['end'],
                           logging.DEBUG : colors['purple'] +
                                          FORMATS['DEFAULT'] +
                                          colors['end'] }
                FORMATS.update( levels )

            def format( self, record ):
                self._fmt = self.FORMATS.get( record.levelno,
                                              self.FORMATS[ 'DEFAULT' ] )
                return logging.Formatter.format( self, record )
        formatter = MyFormatter()
        main.ConsoleHandler.setFormatter(formatter)
        main.LogFileHandler.setFormatter(formatter)

        # add the handlers to logger
        main.log.addHandler(main.ConsoleHandler)
        main.log.addHandler(main.LogFileHandler)

    def testSummary(self,main):
        '''
            testSummary will take care about the Summary of test.
        '''

        main.ENDTIME = datetime.datetime.now()
        main.EXECTIME = main.ENDTIME - main.STARTTIME
        if (main.TOTAL_TC_PASS == 0):
            main.TOTAL_TC_SUCCESS = 0
        else:
            main.TOTAL_TC_SUCCESS = str((main.TOTAL_TC_PASS*100)/main.TOTAL_TC_RUN)
        if (main.TOTAL_TC_RUN == 0) :
            main.TOTAL_TC_EXECPERCENT = 0
        else :
            main.TOTAL_TC_EXECPERCENT = str((main.TOTAL_TC_RUN*100)/main.TOTAL_TC_PLANNED)
        testResult = "\n\n"+"*" * 37+"\n" + "\tTest Execution Summary\n" + "\n"+"*" * 37+" \n"
        testResult =  testResult + "\n Test Start           : " + str(main.STARTTIME.strftime("%d %b %Y %H:%M:%S"))
        testResult =  testResult + "\n Test End             : " + str(main.ENDTIME.strftime("%d %b %Y %H:%M:%S"))
        testResult =  testResult + "\n Execution Time       : " + str(main.EXECTIME)
        testResult =  testResult + "\n Total tests planned  : " + str(main.TOTAL_TC_PLANNED)
        testResult =  testResult + "\n Total tests RUN      : " + str(main.TOTAL_TC_RUN)
        testResult =  testResult + "\n Total Pass           : " + str(main.TOTAL_TC_PASS)
        testResult =  testResult + "\n Total Fail           : " + str(main.TOTAL_TC_FAIL)
        testResult =  testResult + "\n Total No Result      : " + str(main.TOTAL_TC_NORESULT)
        testResult =  testResult + "\n Success Percentage   : " + str(main.TOTAL_TC_SUCCESS) + "%"
        testResult =  testResult + "\n Execution Result     : " + str(main.TOTAL_TC_EXECPERCENT) + "%"

        #main.log.report(testResult)
        main.testResult = testResult
        main.log.exact(testResult)

        ##CSV output needed for Jenkin's plot plugin
        #NOTE: the elements were orded based on the colors assigned to the data
        logfile = open(main.JenkinsCSV ,"w")
        logfile.write(",".join( ['Tests Failed', 'Tests Passed', 'Tests Planned'] ) + "\n")
        logfile.write(",".join( [str(int(main.TOTAL_TC_FAIL)), str(int(main.TOTAL_TC_PASS)), str(int(main.TOTAL_TC_PLANNED))] ))
        logfile.close()

    def updateCaseResults(self,main):
        '''
            Update the case result based on the steps execution and asserting each step in the test-case
        '''
        case = str(main.CurrentTestCaseNumber)
        currentResult = main.testCaseResult.get(case, 2)

        if currentResult == 2:
            main.TOTAL_TC_RUN  = main.TOTAL_TC_RUN + 1
            main.TOTAL_TC_NORESULT = main.TOTAL_TC_NORESULT + 1
            main.log.exact("\n "+"*" * 29+"\n" + "\n Result: No Assertion Called \n"+"*" * 29+"\n")
            line = "Case "+case+": "+main.CurrentTestCase+" - No Result"
        elif currentResult == 1:
            main.TOTAL_TC_RUN  = main.TOTAL_TC_RUN  + 1
            main.TOTAL_TC_PASS =  main.TOTAL_TC_PASS + 1
            main.log.exact("\n"+"*" * 29+"\n Result: Pass \n"+"*" * 29+"\n")
            line = "Case "+case+": "+main.CurrentTestCase+" - PASS"
        elif currentResult == 0:
            main.TOTAL_TC_RUN  = main.TOTAL_TC_RUN  + 1
            main.TOTAL_TC_FAIL = main.TOTAL_TC_FAIL + 1
            main.log.exact("\n"+"*" * 29+"\n Result: Failed \n"+"*" * 29+"\n")
            line = "Case "+case+": "+main.CurrentTestCase+" - FAIL"
        else:
            main.log.error( " Unknown result of case " + case +
                            ". Result was: " + currentResult )
            line = "Case "+case+": "+main.CurrentTestCase+" - ERROR"
        main.log.wiki( "<h3>" + line + "</h3>" )
        main.log.summary( line )

