#!/usr/bin/env python
'''
Created on 26-Dec-2012

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


'''
import re
import sys
class TestParser:
    def __init__(self,testFile):
        try :
            testFileHandler = open(testFile, 'r')
        except IOError:
            print "No such file "+testFile
            sys.exit(0)

        testFileList = testFileHandler.readlines()
        self.testscript = testFileList
        self.caseCode = {}
        self.caseBlock = ''
        self.statementsList = []
        index = 0
        self.statementsList = []
        #initialSpaces = len(line) -len(line.lstrip())
        while index < len(testFileList):
            testFileList[index] = re.sub("^\s{8}|^\s{4}", "", testFileList[index])
            # Skip multiline comments
            if re.match('^(\'\'\')|^(\"\"\")',testFileList[index],0) :
                index = index + 1
                try :
                    while not re.match('^\s*(\'\'\')|^\s*(\"\"\")',testFileList[index],0) :
                        index = index + 1
                except IndexError:
                    print ''

            # skip empty lines and single line comments
            elif not re.match('#|^\s*$',testFileList[index],0):
                self.statementsList.append(testFileList[index])
            index = index + 1

    def case_code(self):
        index = 0
        statementsList = self.statementsList
        while index < len(statementsList):
            m= re.match('def\s+CASE(\d+)',statementsList[index],0)
            self.caseBlock = []
            if m:
                index = index + 1
                try :
                    while not re.match('\s*def\s+CASE(\d+)',statementsList[index],0) :
                        self.caseBlock.append(statementsList[index])
                        if index < len(statementsList)-1:
                            index = index + 1
                        else :
                            break
                    index = index - 1
                except IndexError:
                    print ''
                self.caseCode [str(m.group(1))] = self.caseBlock
            index = index + 1
        return self.caseCode

    def step_code(self,caseStatements):
        index = 0
        step = 0
        stepCode = {}
        step_flag = False
        while index < len(caseStatements):
            m= re.match('main\.step',caseStatements[index],0)
            stepBlock = ''
            if m:
                step_flag = True
                if step == 0 :
                    i = 0
                    block = ''
                    while i < index :
                        block += caseStatements[i]
                        i = i + 1
                    stepCode[step] = block
                    step = step + 1
                stepBlock = stepBlock + caseStatements[index]
                index = index + 1
                try :
                    while not re.match('main\.step',caseStatements[index],0) :
                        stepBlock = stepBlock + caseStatements[index]
                        if index < len(caseStatements)-1:
                            index = index + 1
                        else :
                            break
                    index = index - 1
                except IndexError:
                    print ''
                stepCode[step] = stepBlock
                step = step + 1
            index = index + 1
        # If there is no step defined !!
        if not step_flag :
            stepCode[step] = "".join(caseStatements)
        return stepCode

    def getStepCode(self):
        case_step_code = {}
        case_block = self.case_code()
        for case in case_block :
            case_step_code[case] = {}
            step_block = self.step_code(case_block[case])
            for step in step_block :
                case_step_code[case][step] = step_block[step]
        return case_step_code
