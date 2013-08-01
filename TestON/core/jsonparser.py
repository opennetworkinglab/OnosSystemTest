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

import re
import json
class JsonParser:
    '''
    Module that parses the response Json to Dictionary and Vice versa. 
    '''
    def __init__(self) :
        self.default = ''

    def response_parse(self,json_response):
        '''
         This will parse the json formatted string and return content as Dictionary
        '''
        response_dict = {}
        try :
            response_dict = json.loads(json_response)
        except :
            main.log.error("Json Parser is unable to parse the string")
        return response_dict         
    
    '''
    
    def dict_json(self,response_dict):
        
        # This will parse the Python Dictionary and return content as Json string.
        
        json_response = {}
        try :
            json_response = json.dumps(response_dict)
        except :
            main.log.error("Json Parser is unable to parse the string")
        return json_response  
    '''
