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
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def disconnect(self):
        '''
        Called when Test is complete to disconnect the ONOS handle.
        '''
        response = ''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")
            self.handle.sendline("system:shutdown")
            self.handle.expect("Confirm")
            self.handle.sendline("yes")
            self.handle.expect("\$")

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
        except:
            main.log.error(self.name + ": Connection failed to the host")
            response = main.FALSE
        return response

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
        
    def start_onos_cli(self, ONOS_ip):
        try:
            self.handle.sendline("")
            self.handle.expect("\$")

            #Wait for onos start (-w) and enter onos cli
            self.handle.sendline("onos -w "+str(ONOS_ip))
            self.handle.expect("onos>")

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
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" ::::::")
            main.log.error( traceback.print_exc())
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
        
    def devices(self, json_format=True, grep_str=""):
        '''
        Lists all infrastructure devices
        Optional argument:
            * grep_str - pass in a string to grep
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")
            
            if json_format:
                if not grep_str:
                    self.handle.sendline("devices -j")
                    self.handle.expect("devices -j")
                    self.handle.expect("onos>")
                else:
                    self.handle.sendline("devices -j | grep '"+
                        str(grep_str)+"'")
                    self.handle.expect("devices -j | grep '"+str(grep_str)+"'")
                    self.handle.expect("onos>")
            else:
                if not grep_str:
                    self.handle.sendline("devices")
                    self.handle.expect("onos>")
                    self.handle.sendline("")
                    self.handle.expect("onos>")
                else:
                    self.handle.sendline("devices | grep '"+
                        str(grep_str)+"'")
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

    def links(self, json_format=True, grep_str=""):
        '''
        Lists all core links
        Optional argument:
            * grep_str - pass in a string to grep
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")
            
            if json_format:
                if not grep_str:
                    self.handle.sendline("links -j")
                    self.handle.expect("links -j")
                    self.handle.expect("onos>")
                else:
                    self.handle.sendline("links -j | grep '"+
                        str(grep_str)+"'")
                    self.handle.expect("links -j | grep '"+str(grep_str)+"'")
                    self.handle.expect("onos>")
            else:
                if not grep_str:
                    self.handle.sendline("links")
                    self.handle.expect("onos>")
                    self.handle.sendline("")
                    self.handle.expect("onos>")
                else:
                    self.handle.sendline("links | grep '"+
                        str(grep_str)+"'")
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


    def ports(self, json_format=True, grep_str=""):
        '''
        Lists all ports
        Optional argument:
            * grep_str - pass in a string to grep
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")
            
            if json_format:
                if not grep_str:
                    self.handle.sendline("ports -j")
                    self.handle.expect("ports -j")
                    self.handle.expect("onos>")
                else:
                    self.handle.sendline("ports -j | grep '"+
                        str(grep_str)+"'")
                    self.handle.expect("ports -j | grep '"+str(grep_str)+"'")
                    self.handle.expect("onos>")
            else:
                if not grep_str:
                    self.handle.sendline("ports")
                    self.handle.expect("onos>")
                    self.handle.sendline("")
                    self.handle.expect("onos>")
                else:
                    self.handle.sendline("ports | grep '"+
                        str(grep_str)+"'")
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


    def device_role(self, device_id, node_id, role):
        '''
        Set device role for specified device and node with role
        Required: 
            * device_id : may be obtained by function get_all_devices_id
            * node_id : may be obtained by function get_all_nodes_id
            * role: specify one of the following roles:
                - master
                - standby
                - none
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("device-role "+
                    str(device_id) + " " +
                    str(node_id) + " " +
                    str(role))
            i = self.handle.expect([
                "Error",
                "onos>"])
            
            self.handle.sendline("")
            self.handle.expect("onos>")
    
            handle = self.handle.before

            if i == 0:
                main.log.error("device-role command returned error")
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
    
    #TODO:
    #def hosts(self):

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
            self.handle.sendline("")
            self.handle.expect("onos>")

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

            self.handle.sendline("")
            self.handle.expect("onos>")

            handle = self.handle.before

            main.log.info("Intent installed between "+
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

    def add_point_intent(self, ingress_device, port_ingress,
            egress_device, port_egress):
        '''
        Required:
            * ingress_device: device id of ingress device
            * egress_device: device id of egress device
        Description:
            Adds a point-to-point intent (uni-directional) by
            specifying device id's 
        
        NOTE: This function may change depending on the 
              options developers provide for point-to-point
              intent via cli
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("add-point-intent "+
                    str(ingress_device) + "/" + str(port_ingress) + " " +
                    str(egress_device) + "/" + str(port_egress))
            i = self.handle.expect([
                "Error",
                "onos>"])
            
            self.handle.sendline("")
            self.handle.expect("onos>")

            handle = self.handle.before

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

    def intents(self):
        '''
        Description:
            Obtain intents currently installed 
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("onos>")

            self.handle.sendline("intents")
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

    #***********************************
