#!/usr/bin/env python

'''
This driver enters the onos> prompt to issue commands.

Please follow the coding style demonstrated by existing 
functions and document properly.

If you are a contributor to the driver, please
list your email here for future contact:

jhall@onlab.us
andrew@onlab.us
shreya@onlab.us

OCT 13 2014

'''

import sys
import time
import pexpect
import re
import traceback
import os.path
import pydoc
import re
sys.path.append("../")
from drivers.common.clidriver import CLI

class OnosCliDriver(CLI):

    def __init__(self):
        '''
        Initialize client 
        '''
        super(CLI, self).__init__()

    def connect(self,**connectargs):
        '''
        Creates ssh handle for ONOS cli.
        '''
        try:
            for key in connectargs:
                vars(self)[key] = connectargs[key]
            self.home = "~/ONOS"
            for key in self.options:
                if key == "home":
                    self.home = self.options['home']
                    break


            self.name = self.options['name']
            self.handle = super(OnosCliDriver,self).connect(
                    user_name = self.user_name, 
                    ip_address = self.ip_address,
                    port = self.port, 
                    pwd = self.pwd, 
                    home = self.home)
           
            self.handle.sendline("cd "+ self.home)
            self.handle.expect("\$")
            if self.handle:
                return self.handle
            else :
                main.log.info("NO ONOS HANDLE")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def disconnect(self):
        '''
        Called when Test is complete to disconnect the ONOS handle.
        '''
        response = ''
        try:
            self.handle.sendline("")
            i = self.handle.expect(["onos>","\$"])
            if i == 0:
                self.handle.sendline("system:shutdown")
                self.handle.expect("Confirm")
                self.handle.sendline("yes")
                self.handle.expect("\$")
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline("exit")
            self.handle.expect("closed")

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
        except:
            main.log.error(self.name + ": Connection failed to the host")
            response = main.FALSE
        return response

    def logout(self):
        '''
        Sends 'logout' command to ONOS cli
        '''
        try:
            self.handle.sendline("")
            i = self.handle.expect([
                "onos>",
                "\$"], timeout=10)
            if i == 0:
                self.handle.sendline("logout")
                self.handle.expect("\$")
            elif i == 1:
                return main.TRUE
                    
        except pexpect.EOF:
            main.log.error(self.name + ": eof exception found")
            main.log.error(self.name + ":    " +
                    self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def set_cell(self, cellname):
        '''
        Calls 'cell <name>' to set the environment variables on ONOSbench
        
        Before issuing any cli commands, set the environment variable first.
        '''
        try:
            if not cellname:
                main.log.error("Must define cellname")
                main.cleanup()
                main.exit()
            else:
                self.handle.sendline("cell "+str(cellname))
                #Expect the cellname in the ONOS_CELL variable.
                #Note that this variable name is subject to change
                #   and that this driver will have to change accordingly
                self.handle.expect("ONOS_CELL="+str(cellname))
                handle_before = self.handle.before
                handle_after = self.handle.after
                #Get the rest of the handle
                self.handle.sendline("")
                self.handle.expect("\$")
                handle_more = self.handle.before

                main.log.info("Cell call returned: "+handle_before+
                        handle_after + handle_more)

                return main.TRUE

        except pexpect.EOF:
            main.log.error(self.name + ": eof exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()
        
    def start_onos_cli(self, ONOS_ip, karafTimeout=""):
        '''
        karafTimeout is an optional arugument. karafTimeout value passed by user would be used to set the 
        current karaf shell idle timeout. Note that when ever this property is modified the shell will exit and
        the subsequent login would reflect new idle timeout.
        Below is an example to start a session with 60 seconds idle timeout (input value is in milliseconds):
          
        tValue = "60000"
        main.ONOScli1.start_onos_cli(ONOS_ip, karafTimeout=tValue)
        
        Note: karafTimeout is left as str so that this could be read and passed to start_onos_cli from PARAMS file as str.
        '''
        try:
            self.handle.sendline("")
            x = self.handle.expect([
                "\$", "onos>"], timeout=10)

            if x == 1:
                main.log.info("ONOS cli is already running")
                return main.TRUE

            #Wait for onos start (-w) and enter onos cli
            self.handle.sendline("onos -w "+str(ONOS_ip))
            i = self.handle.expect([
                    "onos>",
                    pexpect.TIMEOUT],timeout=60)

            if i == 0:
                main.log.info(str(ONOS_ip)+" CLI Started successfully")
                if karafTimeout:
                    self.handle.sendline("config:property-set -p org.apache.karaf.shell sshIdleTimeout "+karafTimeout)
                    self.handle.expect("\$")
                    self.handle.sendline("onos -w "+str(ONOS_ip))
                    self.handle.expect("onos>")
                return main.TRUE
            else:
                #If failed, send ctrl+c to process and try again
                main.log.info("Starting CLI failed. Retrying...")
                self.handle.send("\x03")
                self.handle.sendline("onos -w "+str(ONOS_ip))
                i = self.handle.expect(["onos>",pexpect.TIMEOUT],
                        timeout=30)
                if i == 0:
                    main.log.info(str(ONOS_ip)+" CLI Started "+
                        "successfully after retry attempt")
                    if karafTimeout:
                        self.handle.sendline("config:property-set -p org.apache.karaf.shell sshIdleTimeout "+karafTimeout)
                        self.handle.expect("\$")
                        self.handle.sendline("onos -w "+str(ONOS_ip))
			self.handle.expect("onos>")
                    return main.TRUE
                else:
                    main.log.error("Connection to CLI "+\
                        str(ONOS_ip)+" timeout")
                    return main.FALSE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def sendline(self, cmd_str):
        '''
        Send a completely user specified string to 
        the onos> prompt. Use this function if you have 
        a very specific command to send.
        
        Warning: There are no sanity checking to commands
        sent using this method.
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline(cmd_str)
            self.handle.expect("onos>")

            handle = self.handle.before
            
            self.handle.sendline("")
            self.handle.expect("onos>")
            
            handle += self.handle.before
            handle += self.handle.after

            main.log.info("Command sent.")
            ansi_escape = re.compile(r'\x1b[^m]*m')
            handle = ansi_escape.sub('', handle)

            return handle
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    #IMPORTANT NOTE:
    #For all cli commands, naming convention should match
    #the cli command replacing ':' with '_'.
    #Ex) onos:topology > onos_topology
    #    onos:links    > onos_links
    #    feature:list  > feature_list
   
    def add_node(self, node_id, ONOS_ip, tcp_port=""):
        '''
        Adds a new cluster node by ID and address information.
        Required:
            * node_id
            * ONOS_ip
        Optional:
            * tcp_port
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("add-node "+
                    str(node_id)+" "+
                    str(ONOS_ip)+" "+
                    str(tcp_port))
            
            i = self.handle.expect([
                "Error",
                "onos>" ])
            
            #Clear handle to get previous output
            self.handle.sendline("")
            self.handle.expect("onos>")

            handle = self.handle.before

            if i == 0:
                main.log.error("Error in adding node")
                main.log.error(handle)
                return main.FALSE 
            else:
                main.log.info("Node "+str(ONOS_ip)+" added")
                return main.TRUE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def remove_node(self, node_id):
        '''
        Removes a cluster by ID
        Issues command: 'remove-node [<node-id>]'
        Required:
            * node_id
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("remove-node "+str(node_id))
            self.handle.expect("onos>")

            return main.TRUE
        
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def nodes(self):
        '''
        List the nodes currently visible
        Issues command: 'nodes'
        Returns: entire handle of list of nodes
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("nodes")
            self.handle.expect("onos>")

            self.handle.sendline("")
            self.handle.expect("onos>")

            handle = self.handle.before

            return handle

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def topology(self):
        '''
        Shows the current state of the topology
        by issusing command: 'onos> onos:topology'
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")
            #either onos:topology or 'topology' will work in CLI
            self.handle.sendline("onos:topology")
            self.handle.expect("onos>")

            handle = self.handle.before

            main.log.info("onos:topology returned: " +
                    str(handle))
            
            return handle
        
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()
       
    def feature_install(self, feature_str):
        '''
        Installs a specified feature 
        by issuing command: 'onos> feature:install <feature_str>'
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("feature:install "+str(feature_str))
            self.handle.expect("onos>")

            return main.TRUE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.log.report("Failed to install feature")
            main.log.report("Exiting test")
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.report("Failed to install feature")
            main.log.report("Exiting test")
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()
       
    def feature_uninstall(self, feature_str):
        '''
        Uninstalls a specified feature
        by issuing command: 'onos> feature:uninstall <feature_str>'
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("feature:uninstall "+str(feature_str))
            self.handle.expect("onos>")

            return main.TRUE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def devices(self, json_format=True):
        '''
        Lists all infrastructure devices or switches
        Optional argument:
            * json_format - boolean indicating if you want output in json
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            if json_format:
                self.handle.sendline("devices -j")
                self.handle.expect("devices -j")
                self.handle.expect("onos>")
                handle = self.handle.before
                '''
                handle variable here contains some ANSI escape color code sequences at the end which are invisible in the print command output
                To make that escape sequence visible, use repr() function. The repr(handle) output when printed shows the ANSI escape sequences.
                In json.loads(somestring), this somestring variable is actually repr(somestring) and json.loads would fail with the escape sequence.
                So we take off that escape sequence using
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle1 = ansi_escape.sub('', handle)
                '''
                #print "repr(handle) =", repr(handle)
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle1 = ansi_escape.sub('', handle)
                #print "repr(handle1) = ", repr(handle1)
                return handle1
            else:
                self.handle.sendline("devices")
                self.handle.expect("onos>")
                handle = self.handle.before
                #print "handle =",handle
                return handle
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

       
    def balance_masters(self):
        '''
        This balances the devices across all controllers
        by issuing command: 'onos> onos:balance-masters'
        If required this could be extended to return devices balanced output.
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("onos:balance-masters")
            self.handle.expect("onos>")
            return main.TRUE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def links(self, json_format=True):
        '''
        Lists all core links
        Optional argument:
            * json_format - boolean indicating if you want output in json
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            if json_format:
                self.handle.sendline("links -j")
                self.handle.expect("links -j")
                self.handle.expect("onos>")
                handle = self.handle.before
                '''
                handle variable here contains some ANSI escape color code sequences at the end which are invisible in the print command output
                To make that escape sequence visible, use repr() function. The repr(handle) output when printed shows the ANSI escape sequences.
                In json.loads(somestring), this somestring variable is actually repr(somestring) and json.loads would fail with the escape sequence.
                So we take off that escape sequence using
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle1 = ansi_escape.sub('', handle)
                '''
                #print "repr(handle) =", repr(handle)
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle1 = ansi_escape.sub('', handle)
                #print "repr(handle1) = ", repr(handle1)
                return handle1
            else:
                self.handle.sendline("links")
                self.handle.expect("onos>")
                handle = self.handle.before
                #print "handle =",handle
                return handle
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()


    def ports(self, json_format=True):
        '''
        Lists all ports
        Optional argument:
            * json_format - boolean indicating if you want output in json
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            if json_format:
                self.handle.sendline("ports -j")
                self.handle.expect("ports -j")
                self.handle.expect("onos>")
                handle = self.handle.before
                '''
                handle variable here contains some ANSI escape color code sequences at the end which are invisible in the print command output
                To make that escape sequence visible, use repr() function. The repr(handle) output when printed shows the ANSI escape sequences.
                In json.loads(somestring), this somestring variable is actually repr(somestring) and json.loads would fail with the escape sequence.
                So we take off that escape sequence using the following commads:
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle1 = ansi_escape.sub('', handle)
                '''
                #print "repr(handle) =", repr(handle)
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle1 = ansi_escape.sub('', handle)
                #print "repr(handle1) = ", repr(handle1)
                return handle1

            else:
                self.handle.sendline("ports")
                self.handle.expect("onos>")
                self.handle.sendline("")
                self.handle.expect("onos>")
                handle = self.handle.before
                #print "handle =",handle
                return handle
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()


    def roles(self, json_format=True):
        '''
        Lists all devices and the controllers with roles assigned to them
        Optional argument:
            * json_format - boolean indicating if you want output in json
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            if json_format:
                self.handle.sendline("roles -j")
                self.handle.expect("roles -j")
                self.handle.expect("onos>")
                handle = self.handle.before
                '''
                handle variable here contains some ANSI escape color code sequences at the
                end which are invisible in the print command output. To make that escape
                sequence visible, use repr() function. The repr(handle) output when printed
                shows the ANSI escape sequences. In json.loads(somestring), this somestring
                variable is actually repr(somestring) and json.loads would fail with the escape
                sequence.

                So we take off that escape sequence using the following commads:
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle1 = ansi_escape.sub('', handle)
                '''
                #print "repr(handle) =", repr(handle)
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle1 = ansi_escape.sub('', handle)
                #print "repr(handle1) = ", repr(handle1)
                return handle1

            else:
                self.handle.sendline("roles")
                self.handle.expect("onos>")
                self.handle.sendline("")
                self.handle.expect("onos>")
                handle = self.handle.before
                #print "handle =",handle
                return handle
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def get_role(self, device_id):
        '''
        Given the a string containing the json representation of the "roles" cli command and a 
        partial or whole device id, returns a json object containing the
        roles output for the first device whose id contains "device_id"

        Returns:
        Dict of the role assignments for the given device or
        None if not match
        '''
        try:
            import json
            if device_id == None:
                return None
            else:
                raw_roles = self.roles()
                roles_json = json.loads(raw_roles)
                #search json for the device with id then return the device
                for device in roles_json:
                    #print device
                    if str(device_id) in device['id']:
                        return device
            return None

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def roles_not_null(self):
        '''
        Iterates through each device and checks if there is a master assigned
        Returns: main.TRUE if each device has a master
                 main.FALSE any device has no master
        '''
        try:
            import json
            raw_roles = self.roles()
            roles_json = json.loads(raw_roles)
            #search json for the device with id then return the device
            for device in roles_json:
                #print device
                if device['master'] == "none":
                    main.log.warn("Device has no master: " + str(device) )
                    return main.FALSE
            return main.TRUE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()


    def paths(self, src_id, dst_id):
        '''
        Returns string of paths, and the cost.
        Issues command: onos:paths <src> <dst>
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("onos:paths "+
                    str(src_id) + " " + str(dst_id))
            i = self.handle.expect([
                "Error",
                "onos>"])
            
            self.handle.sendline("")
            self.handle.expect("onos>")

            handle = self.handle.before

            if i == 0:
                main.log.error("Error in getting paths")
                return (handle, "Error")
            else:
                path = handle.split(";")[0]
                cost = handle.split(";")[1]
                return (path, cost)
        
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def hosts(self, json_format=True):
        '''
        Lists all discovered hosts
        Optional argument:
            * json_format - boolean indicating if you want output in json
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            if json_format:
                self.handle.sendline("hosts -j")
                self.handle.expect("hosts -j")
                self.handle.expect("onos>")
                handle = self.handle.before
                '''
                handle variable here contains some ANSI escape color code sequences at the end which are invisible in the print command output
                To make that escape sequence visible, use repr() function. The repr(handle) output when printed shows the ANSI escape sequences.
                In json.loads(somestring), this somestring variable is actually repr(somestring) and json.loads would fail with the escape sequence.
                So we take off that escape sequence using
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle1 = ansi_escape.sub('', handle)
                '''
                #print "repr(handle) =", repr(handle)
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle1 = ansi_escape.sub('', handle)
                #print "repr(handle1) = ", repr(handle1)
                return handle1
            else:
                self.handle.sendline("hosts")
                self.handle.expect("onos>")
                handle = self.handle.before
                #print "handle =",handle
                return handle
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def get_host(self, mac):
        '''
        Return the first host from the hosts api whose 'id' contains 'mac'
        Note: mac must be a colon seperated mac address, but could be a partial mac address
        Return None if there is no match
        '''
        import json
        try:
            if mac == None:
                return None
            else:
                mac = mac
                raw_hosts = self.hosts()
                hosts_json = json.loads(raw_hosts)
                #search json for the host with mac then return the device
                for host in hosts_json:
                    #print "%s in  %s?" % (mac, host['id'])
                    if mac in host['id']:
                        return host
            return None
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()


    def get_hosts_id(self, host_list):
        '''
        Obtain list of hosts 
        Issues command: 'onos> hosts'
        
        Required:
            * host_list: List of hosts obtained by Mininet
        IMPORTANT:
            This function assumes that you started your
            topology with the option '--mac'. 
            Furthermore, it assumes that value of VLAN is '-1'
        Description:
            Converts mininet hosts (h1, h2, h3...) into 
            ONOS format (00:00:00:00:00:01/-1 , ...)
        '''
        
        try:
            onos_host_list = []

            for host in host_list:
                host = host.replace("h", "")
                host_hex = hex(int(host)).zfill(12)
                host_hex = str(host_hex).replace('x','0')
                i = iter(str(host_hex))
                host_hex = ":".join(a+b for a,b in zip(i,i))
                host_hex = host_hex + "/-1"
                onos_host_list.append(host_hex) 

            return onos_host_list 

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def add_host_intent(self, host_id_one, host_id_two):
        '''
        Required:
            * host_id_one: ONOS host id for host1
            * host_id_two: ONOS host id for host2
        Description:
            Adds a host-to-host intent (bidrectional) by
            specifying the two hosts.
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("add-host-intent "+
                    str(host_id_one) + " " + str(host_id_two))
            self.handle.expect("onos>")

            handle = self.handle.before
            #print "handle =", handle

            main.log.info("Host intent installed between "+
                    str(host_id_one) + " and " + str(host_id_two))

            return handle

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def add_optical_intent(self, ingress_device, egress_device):
        '''
        Required:
            * ingress_device: device id of ingress device
            * egress_device: device id of egress device
        Optional:
            TODO: Still needs to be implemented via dev side
        ''' 
        try:
            self.handle.sendline("add-optical-intent "+
                    str(ingress_device) + " " + str(egress_device))
            self.handle.expect("add-optical-intent")
            i = self.handle.expect([
                "Error",
                "onos>"])

            handle = self.handle.before

            #If error, return error message
            if i == 0:
                return handle
            else:
                return main.TRUE
        
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def add_point_intent(self, ingress_device, egress_device,
            port_ingress="", port_egress="", ethType="", ethSrc="",
            ethDst="", bandwidth="", lambda_alloc=False, 
            ipProto="", ipSrc="", ipDst="", tcpSrc="", tcpDst=""):
        '''
        Required:
            * ingress_device: device id of ingress device
            * egress_device: device id of egress device
        Optional:
            * ethType: specify ethType
            * ethSrc: specify ethSrc (i.e. src mac addr)
            * ethDst: specify ethDst (i.e. dst mac addr)
            * bandwidth: specify bandwidth capacity of link
            * lambda_alloc: if True, intent will allocate lambda 
              for the specified intent
            * ipProto: specify ip protocol 
            * ipSrc: specify ip source address
            * ipDst: specify ip destination address
            * tcpSrc: specify tcp source port
            * tcpDst: specify tcp destination port
        Description:
            Adds a point-to-point intent (uni-directional) by
            specifying device id's and optional fields

        NOTE: This function may change depending on the 
              options developers provide for point-to-point
              intent via cli
        '''
        try:
            cmd = ""

            #If there are no optional arguments
            if not ethType and not ethSrc and not ethDst\
                    and not bandwidth and not lambda_alloc \
                    and not ipProto and not ipSrc and not ipDst \
                    and not tcpSrc and not tcpDst:
                cmd = "add-point-intent"
      

            else:
                cmd = "add-point-intent"
                
                if ethType:
                    cmd += " --ethType " + str(ethType)
                if ethSrc:
                    cmd += " --ethSrc " + str(ethSrc) 
                if ethDst:    
                    cmd += " --ethDst " + str(ethDst) 
                if bandwidth:
                    cmd += " --bandwidth " + str(bandwidth)
                if lambda_alloc:
                    cmd += " --lambda "
                if ipProto:
                    cmd += " --ipProto " + str(ipProto)
                if ipSrc:
                    cmd += " --ipSrc " + str(ipSrc)
                if ipDst:
                    cmd += " --ipDst " + str(ipDst)
                if tcpSrc:
                    cmd += " --tcpSrc " + str(tcpSrc)
                if tcpDst:
                    cmd += " --tcpDst " + str(tcpDst)

            #Check whether the user appended the port 
            #or provided it as an input
            if "/" in ingress_device:
                cmd += " "+str(ingress_device) 
            else:
                if not port_ingress:
                    main.log.error("You must specify "+
                        "the ingress port")
                    #TODO: perhaps more meaningful return
                    return main.FALSE

                cmd += " "+ \
                    str(ingress_device) + "/" +\
                    str(port_ingress) + " " 

            if "/" in egress_device:
                cmd += " "+str(egress_device)
            else:
                if not port_egress:
                    main.log.error("You must specify "+
                        "the egress port")
                    return main.FALSE
                
                cmd += " "+\
                    str(egress_device) + "/" +\
                    str(port_egress)  

            self.handle.sendline(cmd)
            
            main.log.info(cmd + " sent")
            i = self.handle.expect([
                "Error",
                "onos>"])

            if i == 0:
                main.log.error("Error in adding point-to-point intent")
                return handle
            else:
                return main.TRUE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()


    def add_multipoint_to_singlepoint_intent(self, ingress_device1, ingress_device2,egress_device,
            port_ingress="", port_egress="", ethType="", ethSrc="",
            ethDst="", bandwidth="", lambda_alloc=False, 
            ipProto="", ipSrc="", ipDst="", tcpSrc="", tcpDst="", setEthSrc="", setEthDst=""):
        '''
        Note:
            This function assumes that there would be 2 ingress devices and one egress device
            For more number of ingress devices, this function needs to be modified
        Required:
            * ingress_device1: device id of ingress device1
            * ingress_device2: device id of ingress device2
            * egress_device: device id of egress device
        Optional:
            * ethType: specify ethType
            * ethSrc: specify ethSrc (i.e. src mac addr)
            * ethDst: specify ethDst (i.e. dst mac addr)
            * bandwidth: specify bandwidth capacity of link
            * lambda_alloc: if True, intent will allocate lambda 
              for the specified intent
            * ipProto: specify ip protocol 
            * ipSrc: specify ip source address
            * ipDst: specify ip destination address
            * tcpSrc: specify tcp source port
            * tcpDst: specify tcp destination port
            * setEthSrc: action to Rewrite Source MAC Address
            * setEthDst: action to Rewrite Destination MAC Address
        Description:
            Adds a multipoint-to-singlepoint intent (uni-directional) by
            specifying device id's and optional fields

        NOTE: This function may change depending on the 
              options developers provide for multipointpoint-to-singlepoint
              intent via cli
        '''
        try:
            cmd = ""

            #If there are no optional arguments
            if not ethType and not ethSrc and not ethDst\
                    and not bandwidth and not lambda_alloc \
                    and not ipProto and not ipSrc and not ipDst \
                    and not tcpSrc and not tcpDst and not setEthSrc and not setEthDst:
                cmd = "add-multi-to-single-intent"
      

            else:
                cmd = "add-multi-to-single-intent"
                
                if ethType:
                    cmd += " --ethType " + str(ethType)
                if ethSrc:
                    cmd += " --ethSrc " + str(ethSrc) 
                if ethDst:    
                    cmd += " --ethDst " + str(ethDst) 
                if bandwidth:
                    cmd += " --bandwidth " + str(bandwidth)
                if lambda_alloc:
                    cmd += " --lambda "
                if ipProto:
                    cmd += " --ipProto " + str(ipProto)
                if ipSrc:
                    cmd += " --ipSrc " + str(ipSrc)
                if ipDst:
                    cmd += " --ipDst " + str(ipDst)
                if tcpSrc:
                    cmd += " --tcpSrc " + str(tcpSrc)
                if tcpDst:
                    cmd += " --tcpDst " + str(tcpDst)
                if setEthSrc:
                    cmd += " --setEthSrc "+ str(setEthSrc)
                if setEthDst:
                    cmd += " --setEthDst "+ str(setEthDst)

            #Check whether the user appended the port 
            #or provided it as an input
            if "/" in ingress_device1:
                cmd += " "+str(ingress_device1) 
            else:
                if not port_ingress1:
                    main.log.error("You must specify "+
                        "the ingress port1")
                    #TODO: perhaps more meaningful return
                    return main.FALSE

                cmd += " "+ \
                    str(ingress_device1) + "/" +\
                    str(port_ingress1) + " " 

            if "/" in ingress_device2:
                cmd += " "+str(ingress_device2)
            else:
                if not port_ingress2:
                    main.log.error("You must specify "+
                        "the ingress port2")
                    #TODO: perhaps more meaningful return
                    return main.FALSE

                cmd += " "+ \
                    str(ingress_device2) + "/" +\
                    str(port_ingress2) + " "

            if "/" in egress_device:
                cmd += " "+str(egress_device)
            else:
                if not port_egress:
                    main.log.error("You must specify "+
                        "the egress port")
                    return main.FALSE
                
                cmd += " "+\
                    str(egress_device) + "/" +\
                    str(port_egress)  
            print "cmd= ",cmd
            self.handle.sendline(cmd)
            
            main.log.info(cmd + " sent")
            i = self.handle.expect([
                "Error",
                "onos>"])

            if i == 0:
                main.log.error("Error in adding point-to-point intent")
                return self.handle
            else:
                return main.TRUE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()


    def remove_intent(self, intent_id):
        '''
        Remove intent for specified intent id
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("remove-intent "+str(intent_id))
            i = self.handle.expect([
                "Error",
                "onos>"])
           
            handle = self.handle.before

            if i == 0:
                main.log.error("Error in removing intent")
                return handle
            else:
                return handle 
        
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    # This method should be used after installing application: onos-app-sdnip
    def routes(self, json_format=False):
        '''
        Optional:
            * json_format: enable output formatting in json
        Description:
            Obtain all routes in the system
        '''
        try:
            if json_format:
                self.handle.sendline("routes -j")
                self.handle.expect("routes -j")
                self.handle.expect("onos>")
                handle_tmp = self.handle.before
                
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle = ansi_escape.sub('', handle_tmp)

            else:
                self.handle.sendline("")
                self.handle.expect("onos>")

                self.handle.sendline("routes")
                self.handle.expect("onos>")
                handle = self.handle.before

            return handle

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + " ::::::")
            main.log.error(traceback.print_exc())
            main.log.info(self.name + " ::::::")
            main.cleanup()
            main.exit()

    def intents(self, json_format = True):
        '''
        Optional:
            * json_format: enable output formatting in json
        Description:
            Obtain intents currently installed 
        '''
        try:
            if json_format:
                self.handle.sendline("intents -j")
                self.handle.expect("intents -j")
                self.handle.expect("onos>")
                handle = self.handle.before
                
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle = ansi_escape.sub('', handle)
            else:
                self.handle.sendline("")
                self.handle.expect("onos>")

                self.handle.sendline("intents")
                self.handle.expect("onos>")
                handle = self.handle.before

            return handle

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def flows(self, json_format = True):
        '''
        Optional:
            * json_format: enable output formatting in json
        Description:
            Obtain flows currently installed 
        '''
        try:
            if json_format:
                self.handle.sendline("flows -j")
                self.handle.expect("flows -j")
                self.handle.expect("onos>")
                handle = self.handle.before
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle = ansi_escape.sub('', handle)

            else:
                self.handle.sendline("")
                self.handle.expect("onos>")
                self.handle.sendline("flows")
                self.handle.expect("onos>")
                handle = self.handle.before
            if re.search("Error\sexecuting\scommand:", handle):
                main.log.error(self.name + ".flows() response: " + str(handle))

            return handle

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def push_test_intents(self, dpid_src, dpid_dst, num_intents, 
            num_mult="", app_id="", report=True):
        '''
        Description:
            Push a number of intents in a batch format to 
            a specific point-to-point intent definition
        Required:
            * dpid_src: specify source dpid
            * dpid_dst: specify destination dpid
            * num_intents: specify number of intents to push
        Optional:
            * num_mult: number multiplier for multiplying
              the number of intents specified
            * app_id: specify the application id init to further
              modularize the intents
            * report: default True, returns latency information
        '''
        try:
            cmd = "push-test-intents "+\
                  str(dpid_src)+" "+str(dpid_dst)+" "+\
                  str(num_intents)
            
            if num_mult:
                cmd += " " + str(num_mult)
                #If app id is specified, then num_mult 
                #must exist because of the way this command
                #takes in arguments
                if app_id:
                    cmd += " " + str(app_id)
            
            self.handle.sendline(cmd)
            self.handle.expect(cmd)
            self.handle.expect("onos>")
                
            handle = self.handle.before
              
            #Some color thing that we want to escape
            ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
            handle = ansi_escape.sub('', handle)
    
            if report:
                lat_result = []
                main.log.info(handle)
                #Split result by newline
                newline = handle.split("\r\r\n")
                #Ignore the first object of list, which is empty
                newline = newline[1:]
                #Some sloppy parsing method to get the latency
                for result in newline:
                    result = result.split(": ")
                    #Append the first result of second parse
                    lat_result.append(result[1].split(" ")[0])

                main.log.info(lat_result) 
                return lat_result 
            else:
                return main.TRUE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def intents_events_metrics(self, json_format=True):
        '''
        Description:Returns topology metrics 
        Optional:
            * json_format: enable json formatting of output
        '''
        try:
            if json_format:
                self.handle.sendline("intents-events-metrics -j")
                self.handle.expect("intents-events-metrics -j")
                self.handle.expect("onos>")
                
                handle = self.handle.before
              
                #Some color thing that we want to escape
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle = ansi_escape.sub('', handle)
            
            else:
                self.handle.sendline("intents-events-metrics")
                self.handle.expect("intents-events-metrics")
                self.handle.expect("onos>")
                
                handle = self.handle.before

            return handle
        
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def topology_events_metrics(self, json_format=True):
        '''
        Description:Returns topology metrics 
        Optional:
            * json_format: enable json formatting of output
        '''
        try:
            if json_format:
                self.handle.sendline("topology-events-metrics -j")
                self.handle.expect("topology-events-metrics -j")
                self.handle.expect("onos>")
                
                handle = self.handle.before
              
                #Some color thing that we want to escape
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle = ansi_escape.sub('', handle)
            
            else:
                self.handle.sendline("topology-events-metrics")
                self.handle.expect("topology-events-metrics")
                self.handle.expect("onos>")
                
                handle = self.handle.before

            return handle
        
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    #Wrapper functions ****************
    #Wrapper functions use existing driver
    #functions and extends their use case.
    #For example, we may use the output of
    #a normal driver function, and parse it
    #using a wrapper function

    def get_all_intents_id(self):
        '''
        Description:
            Obtain all intent id's in a list
        '''
        try:
            #Obtain output of intents function
            intents_str = self.intents()
            all_intent_list = []
            intent_id_list = []

            #Parse the intents output for ID's
            intents_list = [s.strip() for s in intents_str.splitlines()]
            for intents in intents_list:
                if "onos>" in intents:
                    continue
                elif "intents" in intents:
                    continue
                else:
                    line_list = intents.split(" ")
                    all_intent_list.append(line_list[0])
            
            all_intent_list = all_intent_list[1:-2]

            for intents in all_intent_list:
                if not intents:
                    continue
                else:
                    intent_id_list.append(intents) 

            return intent_id_list

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def get_all_devices_id(self):
        '''
        Use 'devices' function to obtain list of all devices
        and parse the result to obtain a list of all device
        id's. Returns this list. Returns empty list if no
        devices exist
        List is ordered sequentially 
        
        This function may be useful if you are not sure of the
        device id, and wish to execute other commands using 
        the ids. By obtaining the list of device ids on the fly,
        you can iterate through the list to get mastership, etc.
        '''
        try:
            #Call devices and store result string
            devices_str = self.devices(json_format=False)
            id_list = []
            
            if not devices_str:
                main.log.info("There are no devices to get id from")
                return id_list
           
            #Split the string into list by comma
            device_list = devices_str.split(",")
            #Get temporary list of all arguments with string 'id='
            temp_list = [dev for dev in device_list if "id=" in dev]
            #Split list further into arguments before and after string
            # 'id='. Get the latter portion (the actual device id) and
            # append to id_list
            for arg in temp_list:
                id_list.append(arg.split("id=")[1])
            return id_list

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def get_all_nodes_id(self):
        '''
        Uses 'nodes' function to obtain list of all nodes
        and parse the result of nodes to obtain just the
        node id's. 
        Returns:
            list of node id's
        '''
        try:
            nodes_str = self.nodes()
            id_list = []

            if not nodes_str:
                main.log.info("There are no nodes to get id from")
                return id_list

            #Sample nodes_str output
            #id=local, address=127.0.0.1:9876, state=ACTIVE *

            #Split the string into list by comma
            nodes_list = nodes_str.split(",")
            temp_list = [node for node in nodes_list if "id=" in node]
            for arg in temp_list:
                id_list.append(arg.split("id=")[1])

            return id_list
        
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def get_device(self, dpid=None):
        '''
        Return the first device from the devices api whose 'id' contains 'dpid'
        Return None if there is no match
        '''
        import json
        try:
            if dpid == None:
                return None
            else:
                dpid = dpid.replace(':', '')
                raw_devices = self.devices()
                devices_json = json.loads(raw_devices)
                #search json for the device with dpid then return the device
                for device in devices_json:
                    #print "%s in  %s?" % (dpid, device['id'])
                    if dpid in device['id']:
                        return device
            return None
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def check_status(self, ip, numoswitch, numolink, log_level="info"):
        '''
        Checks the number of swithes & links that ONOS sees against the 
        supplied values. By default this will report to main.log, but the 
        log level can be specifid.
        
        Params: ip = ip used for the onos cli
                numoswitch = expected number of switches
                numlink = expected number of links
                log_level = level to log to. Currently accepts 'info', 'warn' and 'report'


        log_level can

        Returns: main.TRUE if the number of switchs and links are correct, 
                 main.FALSE if the numer of switches and links is incorrect,
                 and main.ERROR otherwise
        '''

        try:
            topology = self.get_topology(ip)
            if topology == {}:
                return main.ERROR
            output = ""
            #Is the number of switches is what we expected
            devices = topology.get('devices',False)
            links = topology.get('links',False)
            if devices == False or links == False:
                return main.ERROR
            switch_check = ( int(devices) == int(numoswitch) )
            #Is the number of links is what we expected
            link_check = ( int(links) == int(numolink) )
            if (switch_check and link_check):
                #We expected the correct numbers
                output = output + "The number of links and switches match "\
                        + "what was expected"
                result = main.TRUE
            else:
                output = output + \
                        "The number of links and switches does not match what was expected"
                result = main.FALSE
            output = output + "\n ONOS sees %i devices (%i expected) and %i links (%i expected)"\
                    % ( int(devices), int(numoswitch), int(links), int(numolink) )
            if log_level == "report":
                main.log.report(output)
            elif log_level == "warn":
                main.log.warn(output)
            else:
                main.log.info(output)
            return result 
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def device_role(self, device_id, onos_node, role="master"):
        '''
        Calls the device-role cli command.
        device_id must be the id of a device as seen in the onos devices command
        onos_node is the ip of one of the onos nodes in the cluster
        role must be either master, standby, or none

        Returns main.TRUE or main.FALSE based on argument verification.
            When device-role supports errors this should be extended to
            support that output
        '''
        try:
            #print "beginning device_role... \n\tdevice_id:" + device_id
            #print "\tonos_node: " + onos_node
            #print "\trole: "+ role
            if role.lower() == "master" or \
                    role.lower() == "standby" or \
                    role.lower() == "none":
                        self.handle.sendline("")
                        self.handle.expect("onos>")
                        self.handle.sendline("device-role " +
                                str(device_id) + " " +
                                str(onos_node) +  " " +
                                str(role))
                        i= self.handle.expect(["Error","onos>"])
                        if i == 0:
                            output = str(self.handle.before)
                            self.handle.expect("onos>")
                            output = output + str(self.handle.before)
                            main.log.error(self.name + ": " +
                                    output + '\033[0m')#end color output to escape any colours from the cli
                            return main.ERROR
                        self.handle.sendline("")
                        self.handle.expect("onos>")
                        return main.TRUE
            else:
                return main.FALSE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def clusters(self, json_format=True):
        '''
        Lists all clusters
        Optional argument:
            * json_format - boolean indicating if you want output in json
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            if json_format:
                self.handle.sendline("clusters -j")
                self.handle.expect("clusters -j")
                self.handle.expect("onos>")
                handle = self.handle.before
                '''
                handle variable here contains some ANSI escape color code
                sequences at the end which are invisible in the print command
                output. To make that escape sequence visible, use repr() function.
                The repr(handle) output when printed shows the ANSI escape sequences.
                In json.loads(somestring), this somestring variable is actually
                repr(somestring) and json.loads would fail with the escape sequence.
                So we take off that escape sequence using
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle1 = ansi_escape.sub('', handle)
                '''
                #print "repr(handle) =", repr(handle)
                ansi_escape = re.compile(r'\r\r\n\x1b[^m]*m')
                handle1 = ansi_escape.sub('', handle)
                #print "repr(handle1) = ", repr(handle1)
                return handle1
            else:
                self.handle.sendline("clusters")
                self.handle.expect("onos>")
                handle = self.handle.before
                #print "handle =",handle
                return handle
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def election_test_leader(self):
        '''
         * CLI command to get the current leader for the Election test application.
         #NOTE: Requires installation of the onos-app-election feature
         Returns: Node IP of the leader if one exists
                  None if none exists
                  Main.FALSE on error
        '''
        try:
            self.handle.sendline("election-test-leader")
            self.handle.expect("election-test-leader")
            self.handle.expect("onos>")
            response = self.handle.before
            #Leader
            node_search = re.search("The\scurrent\sleader\sfor\sthe\sElection\sapp\sis\s(?P<node>.+)\.", response)
            if node_search:
                node = node_search.group('node')
                main.log.info("Election-test-leader on "+str(self.name)+" found " + node + " as the leader")
                return node
            #no leader
            null_search = re.search("There\sis\scurrently\sno\sleader\selected\sfor\sthe\sElection\sapp", response)
            if null_search:
                main.log.info("Election-test-leader found no leader on " + self.name )
                return None
            #error
            if re.search("Command\snot\sfound", response):
                main.log.error("Election app is not loaded on " + self.name)
                return main.FALSE
            else:
                main.log.error("Error in election_test_leader: unexpected response")
                main.log.error( repr(response) )
                return main.FALSE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def election_test_run(self):
        '''
         * CLI command to run for leadership of the Election test application.
         #NOTE: Requires installation of the onos-app-election feature
         Returns: Main.TRUE on success
                  Main.FALSE on error
        '''
        try:
            self.handle.sendline("election-test-run")
            self.handle.expect("election-test-run")
            self.handle.expect("onos>")
            response = self.handle.before
            #success
            search = re.search("Entering\sleadership\selections\sfor\sthe\sElection\sapp.", response)
            if search:
                main.log.info(self.name + " entering leadership elections for the Election app.")
                return main.TRUE
            #error
            if re.search("Command\snot\sfound", response):
                main.log.error("Election app is not loaded on " + self.name)
                return main.FALSE
            else:
                main.log.error("Error in election_test_run: unexpected response")
                main.log.error( repr(response) )
                return main.FALSE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def election_test_withdraw(self):
        '''
         * CLI command to withdraw the local node from leadership election for
         * the Election test application.
         #NOTE: Requires installation of the onos-app-election feature
         Returns: Main.TRUE on success
                  Main.FALSE on error
        '''
        try:
            self.handle.sendline("election-test-withdraw")
            self.handle.expect("election-test-withdraw")
            self.handle.expect("onos>")
            response = self.handle.before
            #success
            search = re.search("Withdrawing\sfrom\sleadership\selections\sfor\sthe\sElection\sapp.", response)
            if search:
                main.log.info(self.name + " withdrawing from leadership elections for the Election app.")
                return main.TRUE
            #error
            if re.search("Command\snot\sfound", response):
                main.log.error("Election app is not loaded on " + self.name)
                return main.FALSE
            else:
                main.log.error("Error in election_test_withdraw: unexpected response")
                main.log.error( repr(response) )
                return main.FALSE


        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    #***********************************
    def getDevicePortsEnabledCount(self,dpid):
        '''
        Get the count of all enabled ports on a particular device/switch
        '''
        try:
            dpid = str(dpid)
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("onos:ports -e "+dpid+" | wc -l")
            i = self.handle.expect([
                "No such device",
                "onos>"])
            
            #self.handle.sendline("")
            #self.handle.expect("onos>")

            output = self.handle.before

            if i == 0:
                main.log.error("Error in getting ports")
                return (ouput, "Error")
            else:
                result = output
                return result
        
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def getDeviceLinksActiveCount(self,dpid):
        '''
        Get the count of all enabled ports on a particular device/switch
        '''
        try:
            dpid = str(dpid)
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("onos:links "+dpid+" | grep ACTIVE | wc -l")
            i = self.handle.expect([
                "No such device",
                "onos>"])

            output = self.handle.before

            if i == 0:
                main.log.error("Error in getting ports")
                return (ouput, "Error")
            else:
                result = output
                return result
        
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()

    def getAllIntentIds(self):
        '''
        Return a list of all Intent IDs
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("onos:intents | grep id=")
            i = self.handle.expect([
                "Error",
                "onos>"])

            output = self.handle.before

            if i == 0:
                main.log.error("Error in getting ports")
                return (ouput, "Error")
            else:
                result = output
                return result
        
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" ::::::")
            main.cleanup()
            main.exit()
