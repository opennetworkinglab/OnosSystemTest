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

import xmldict
import re

class xmlparser :

    def __init__(self) :
        self.default = ''

    def parse(self,fileName) :
        '''
         This will parse the params or topo or cfg file and return content in the file as Dictionary
        '''
        self.fileName = fileName
        matchFileName = re.match(r'(.*)\.(params|topo|cfg)', self.fileName, re.M | re.I)
        if matchFileName:
            xml = open(fileName).read()
            try :
                parsedInfo = xmldict.xml_to_dict(xml)
                return parsedInfo
            except StandardError as e:
                print "Error parsing file " + fileName + ": " + e.message
        else :
            print "File name is not correct"

    def parseParams(self,paramsPath):
        '''
         It will take the params file path and will return the params dictionary
        '''
        paramsPath = re.sub("\.","/",paramsPath)
        paramsPath = re.sub("tests|examples","",paramsPath)
        params = self.parse(main.tests_path+paramsPath+".params")
        paramsAsString = str(params)
        return eval(paramsAsString)

    def parseTopology(self,topologyPath):
        '''
          It will take topology file path and will return topology dictionary
        '''
        topologyPath = re.sub("\.","/",topologyPath)
        topologyPath = re.sub("tests|examples","",topologyPath)
        #topology = self.parse(main.tests_path+"/"+topologyPath+".topo")
        topology = self.parse(main.tests_path+topologyPath+".topo")
        topoAsString = str(topology)
        return eval(topoAsString)

