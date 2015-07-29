#!/usr/bin/env python
'''
Created on 11-Oct-2012

@authors: Anil Kumar (anilkumar.s@paxterrasolutions.com),

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
import pexpect
import struct, fcntl, os, sys, signal
import re
from core import xmldict

class GenerateDriver():
    '''
        This will
    '''
    def __init__(self):
        self.default = ''
        self.prompt = '>'
        self.LASTRSP =''
        self.command_dictionary  = {}
        self.config_details = {}
        self.last_sub_command = None
        self.commnads_ordered_list = []
        filePath = "generatedriver.cfg"
        self.configFile = filePath
        try :
            xml = open(filePath).read()
            self.config_details = xmldict.xml_to_dict(xml)
        except :
            print "Error : Config file " + self.configFile + " not defined properly or file path error"
            sys.exit()
        print self.config_details
        self.device_name = ''

    def connect(self,**connectargs):
        '''
           Connection will establish to the remote host using ssh.
           It will take user_name ,ip_address and password as arguments<br>
           and will return the handle.
        '''
        for key in connectargs:
            vars(self)[key] = connectargs[key]

        ssh_newkey = 'Are you sure you want to continue connecting'
        refused = "ssh: connect to host "+self.ip_address+" port 22: Connection refused"
        if self.port:
            self.handle =pexpect.spawn('ssh -p '+self.port+' '+self.user_name+'@'+self.ip_address,maxread=50000)
        else :
            self.handle =pexpect.spawn('ssh '+self.user_name+'@'+self.ip_address,maxread=50000)

        self.logfile_handler = open(os.getcwd()+"/GenerateDriver.log","w+")
        self.handle.logfile = self.logfile_handler
        i=self.handle.expect([ssh_newkey,'password:',pexpect.EOF,pexpect.TIMEOUT,refused],10)

        if i==0:
            self.handle.sendline('yes')
            i=self.handle.expect([ssh_newkey,'password:',pexpect.EOF,pexpect.TIMEOUT])
            return self.handle
        if i==1:
            self.handle.sendline(self.pwd)
            self.handle.expect('>|#|$')
            return self.handle
        elif i==2:
            print "ssh: connect to host "+self.ip_address+": Error"
            return False
        elif i==3: #timeout

            print "ssh: connect to host "+self.ip_address+": Connection timed out"
            return False
        elif i==4:
            print "ssh: connect to host "+self.ip_address+": Connection refused"
            return False

        self.handle.sendline("\r")
        return self.handle

    def execute(self, **execparams):
        '''
        This method will execute the command and will check for the expected prompt.
        '''
        self.LASTRSP = ''
        defaultPrompt = '.*[\$>\#]'
        for key in execparams:
            vars(self)[key] = execparams[key]

        self.handle.sendline(self.cmd)
        timeoutVar = self.timeout if self.timeout else 10

        index = self.handle.expect([self.prompt, "byte\s\d+", 'Command not found.', pexpect.TIMEOUT,"\n:",pexpect.EOF], timeout = timeoutVar)
        if index == 0:
            self.LASTRSP = self.LASTRSP + self.handle.before
            #print "Expected Prompt Found"
        elif index == 1:
            self.LASTRSP = self.LASTRSP + self.handle.before
            self.handle.send("\r")
            print("Found More screen to go , Sending a key to proceed")
            indexMore = self.handle.expect(["byte\s\d+", self.prompt], timeout = timeoutVar)
            while indexMore == 0:
                print "Found another More screen to go , Sending a key to proceed"
                self.handle.send("\r")
                indexMore = self.handle.expect(["byte\s\d+", self.prompt,pexpect.EOF,pexpect.TIMEOUT], timeout = timeoutVar)
                self.LASTRSP = self.LASTRSP + self.handle.before
            #print self.LASTRSP
        elif index ==2:
            print "Command not found"
            self.LASTRSP = self.LASTRSP + self.handle.before
        elif index ==3:
            print "Expected Prompt not found , Time Out!!"
            return False
        elif index == 4:

            self.LASTRSP = self.LASTRSP + self.handle.before
            self.handle.sendcontrol("D")
            #print "AA"*89
            indexMore = self.handle.expect(["\n:", self.prompt,pexpect.EOF,pexpect.TIMEOUT], timeout = timeoutVar)
            while indexMore == 0:
                self.handle.sendcontrol("D")

                indexMore = self.handle.expect(["\n:", self.prompt,".*",pexpect.EOF,pexpect.TIMEOUT], timeout = timeoutVar)
                self.LASTRSP = self.LASTRSP + self.handle.before

        return self.LASTRSP

    def configure(self):
        '''
        Will start the Configure mode of the device.
        '''
        config_result = self.execute(cmd="configure",prompt='\#',timeout=10)
        return config_result

    def get_command_help(self,command):
        '''
        Will get the help of the Command
        '''

        self.handle.setecho(False)
        help_keyword = self.config_details['device'][self.device_name]['help_keyword']
        interrupt_key = self.config_details['device'][self.device_name]['interrupt_key']
        command_details = self.execute(cmd=command+" "+help_keyword,prompt='\#',timeout=2)
        #command_details = self.execute(cmd=command+" "+help_keyword,prompt='\#',timeout=2)
        self.handle.sendcontrol(interrupt_key)
        #print command_details
        return command_details

    def get_command_details(self,command):
        '''
        Will Update the command_dictionary with the available commands details
        '''

        temp_dictionary = {}
        command_resulut = self.get_command_help(command)
        try :
            words = command_resulut.split("\n")
        except AttributeError,e:
            print e
            return
        lines = command_resulut.split("\n")
        options_list = []
        for line in lines :
            value_match = re.search('[\s|\>|\+|\-|\<]{3}(\<(\w+))\s*',line)
            if value_match:
                print " Enter Value for "+value_match.group(2)
                #self.handle.interact()
            else:
                match = re.search(r"\s\s[\w|-]+\s\s",line)
                if match :
                    match_command = match.group(0)
                    print match_command
                    options_list.append(match_command)

        temp_dictionary[command] = options_list
        self.command_dictionary[command] = options_list
        self.print_details(self.command_dictionary)
        print "temp dir: --------"
        print temp_dictionary
        print "-------------"
        return temp_dictionary

    def print_details(self,command_dictionary):
        '''
        Will print the details in Tree Format
        '''
        self.commnads_ordered_list = command_dictionary.keys()
        # Sorting the output based on the length of the command string
        length = len(self.commnads_ordered_list ) - 1
        sorted = False

        while not sorted:
            sorted = True
            for i in range(length):
                if len(self.commnads_ordered_list[i]) > len(self.commnads_ordered_list[i+1]):
                    sorted = False
                    self.commnads_ordered_list[i], self.commnads_ordered_list[i+1] = self.commnads_ordered_list[i+1], self.commnads_ordered_list[i]

        for key in self.commnads_ordered_list:
            print key +"\t "+str(command_dictionary[key])
        print "\n\n"


    def get_details_recursive(self,main_comand):
        try :
            self.last_sub_command = main_comand.split()[len(main_comand.split())-1]
        except :
            self.last_sub_command = ''
        main_result_dcitionary = self.get_command_details(main_comand)
        if main_result_dcitionary :
            for key in main_result_dcitionary.keys():
                for index, each_option in enumerate(main_result_dcitionary[key]) :

                    if re.search(self.config_details['device'][self.device_name]['end_pattern']+"|^\.|^\d",str(main_result_dcitionary[key][index])):
                        print "Reached the last argument for this "+main_comand+" "+str(each_option)+"\n"
                        main_result_dcitionary[key].remove(each_option)
                        return
                    elif self.last_sub_command == str(main_result_dcitionary[key][index]):
                        print "Same command repeating, So Exiting "+main_comand+" "+str(each_option)+"\n"
                        main_result_dcitionary[key].remove(each_option)
                        break
                    result_dcitionary = self.get_details_recursive(main_comand+" "+str(each_option))

        return
    def create_driver(self):
        name = self.device_name
        driver_file_data = 'class '+name +":\n"
        driver_file_data = driver_file_data + "    def __init__( self ):\n"
        driver_file_data = driver_file_data + "        self.prompt = '(.*)'\n        self.timeout = 60 \n\n"

        for index,command in enumerate(self.commnads_ordered_list) :
            api_data = '    def '
            command_as_api = re.sub(" ","_" , command, 0)
            command_as_api = re.sub("\.|\-|\\|\/|\/","" , command_as_api, 0)
            current_letter = 0
            underscore_count = 0
            command_temp = ""
            for c in command_as_api:
                current_letter = current_letter + 1
                if c == "_":
                    underscore_count = underscore_count+1
                else:
                    underscore_count = 0
                if underscore_count > 1:
                   command_temp = command_temp + ""
                else:
                   command_temp = command_temp + c
            if command_temp[len(command_temp)-1] == "_":
                command_temp = command_temp[0:len(command_temp)-1]
            command_as_api = command_temp
            #options = ''
            #for option in self.command_dictionary[command]:
                #options = options+',' + option

            #options = re.sub("^\s*,|,$","" , options, 0)
            api_data = api_data + command_as_api+"(self, *options, **def_args ):\n"
            api_data = api_data + "        '''Possible Options :"+str(self.command_dictionary[command])+"'''\n"
            api_data = api_data + "        arguments= ''\n"
            api_data = api_data + "        for option in options:\n"
            api_data = api_data + "            arguments = arguments + option +' ' \n"
            api_data = api_data + "        prompt = def_args.setdefault('prompt',self.prompt)\n"
            api_data = api_data + "        timeout = def_args.setdefault('timeout',self.timeout)\n"

            api_data = api_data + "        self.execute( cmd= \""+ command + " \"+ arguments, prompt = prompt, timeout = timeout ) \n"
            api_data = api_data + "        return main.TRUE\n"

            driver_file_data = driver_file_data +  api_data +"\n"
        driver_file = open(os.getcwd()+"/"+name.lower()+".py", 'w')
        driver_file.write(driver_file_data)
        print driver_file_data

    def disconnect(self):
        result = True
        return result

    import pexpect

if __name__ == "__main__":

    generate = GenerateDriver()
    import sys
    device_name = sys.argv[1]
    generate.device_name = device_name
    ip_address = generate.config_details['device'][device_name]['ip_address']
    user_name = generate.config_details['device'][device_name]['user_name']
    password  = generate.config_details['device'][device_name]['password']
    command = generate.config_details['device'][device_name]['command']
    commandlist = re.sub("(\[|\])", "", command)
    commandlist = list(eval(command+','))
    connect_handle = generate.connect(user_name = user_name ,ip_address = ip_address, pwd = password , port = None)
    if connect_handle :
   #     generate.configure()

        for root_command in commandlist :
            generate.get_details_recursive(root_command)

        generate.create_driver()
        generate.disconnect()
        #generate.get_command_details(main_command)
    else :
        print "Connection Failed to the host"


