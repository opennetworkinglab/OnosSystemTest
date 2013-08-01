#!/usr/bin/env python
'''
Created on 24-June-2013 

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
import time
import pexpect
import struct, fcntl, os, sys, signal
import sys
import re
sys.path.append("../")
from drivers.common.clidriver import CLI

class HPSwitch(CLI):
    
    def __init__(self):
        super(CLI, self).__init__()
        
    def connect(self,**connectargs):
        for key in connectargs:
           vars(self)[key] = connectargs[key]

        self.name = self.options['name']
        self.handle = super(HPSwitch,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd)

        return main.TRUE

    def configure(self):
        self.execute(cmd='configure', prompt = '\(config\)',timeout = 3)
        if re.search('\(config\)', main.last_response):
            main.log.info("Configure mode enabled"+main.last_response)
        else : 
            main.log.warn("Fail to enable configure mode"+main.last_response)
        

    def set_up_vlan(self,**vlanargs):
        '''
        Configure vlan.
        '''
        for key in vlanargs:
           vars(self)[key] = vlanargs[key]
           
        self.execute(cmd='vlan '+self.vlan_id, prompt = '\(vlan-'+self.vlan_id+'\)',timeout = 3)
        if re.search('\(vlan-'+self.vlan_id+'\)', main.last_response):
            main.log.info("Configuring VLAN "+self.vlan_id)
        else : 
            main.log.warn("Fail to configure Vlan"+self.vlan_id+main.last_response)
            return main.FALSE
        
        if self.vlan_name :
            self.execute(cmd='name '+self.vlan_name, prompt = '\(vlan-'+self.vlan_id+'\)',timeout = 3)
            if re.search('\(vlan-'+self.vlan_id+'\)', main.last_response):
                main.log.info("Configuring "+self.vlan_id)
                return main.TRUE
            else : 
                main.log.warn("Fail to configure Vlan"+self.vlan_id+main.last_response)
                return main.FALSE
        else :
            main.log.error("Vlan Name not specified")
            return main.FALSE
        
    def vlan_tagged(self, **taggedargs):
        for key in taggedargs:
           vars(self)[key] = taggedargs[key]
        if self.vlan_id :
            self.execute(cmd='vlan '+self.vlan_id, prompt = '\(vlan-'+self.vlan_id+'\)',timeout = 3)
            
            if re.search('\(vlan-'+self.vlan_id+'\)', main.last_response):
                main.log.info("Configuring "+self.vlan_id)
            else : 
                main.log.warn("Fail to configure Vlan"+self.vlan_id+main.last_response)
                return main.FALSE
            if self.tagged :
                self.execute(cmd='tagged '+self.vlan_id, prompt = '\(vlan-'+self.vlan_id+'\)',timeout = 3)
                if re.search('\(vlan-'+self.vlan_id+'\)', main.last_response):
                    main.log.info("VLAN tagged done "+self.tagged)
                    return main.TRUE
                else : 
                    main.log.warn("Fail to tagged Vlan"+self.vlan_id+main.last_response)
                    return main.FALSE
            
    def vlan_untagged(self, **untaggedargs):
        for key in untaggedargs:
           vars(self)[key] = untaggedargs[key]
        if self.vlan_id :
            self.execute(cmd='vlan '+self.vlan_id, prompt = '\(vlan-'+self.vlan_id+'\)',timeout = 3)
            
            if re.search('\(vlan-'+self.vlan_id+'\)', main.last_response):
                main.log.info("Configuring "+self.vlan_id)
            else : 
                main.log.warn("Fail to configure Vlan"+self.vlan_id+main.last_response)
                return main.FALSE
            if self.tagged :
                self.execute(cmd='untagged '+self.vlan_id, prompt = '\(vlan-'+self.vlan_id+'\)',timeout = 3)
                if re.search('\(vlan-'+self.vlan_id+'\)', main.last_response):
                    main.log.info("VLAN untagged done "+self.tagged)
                    return main.TRUE
                else : 
                    main.log.warn("Fail to untagged Vlan"+self.vlan_id+main.last_response)
                    return main.FALSE
                
    def openflow_mode(self):
        self.configure()
        self.execute(cmd='openflow', prompt = '\(openflow\)',timeout = 3)
        if re.search('\(openflow\)', main.last_response):
            main.log.info("Openflow mode enabled"+main.last_response)
            return main.TRUE
        else : 
            main.log.warn("Fail to enable Openflow mode"+main.last_response)
            return main.FALSE


    def add_openflow_controller(self,**controllerargs):
        for key in controllerargs:
           vars(self)[key] = controllerargs[key]
           
        if not self.openflow_mode():
            return main.FALSE
            
        contoller_details = 'controller-id '+ self.controller_id+'ip '+self.controller_ip + 'controller-interface vlan '+self.interface_vlan_id  
        self.execute(cmd=contoller_details, prompt = '\(openflow\)',timeout = 3)
        
        if re.search('already\sconfigured', main.last_response):
            main.log.warn("A controller is already configured with this ID."+main.last_response)
            return main.FALSE
        elif re.search('Incomplete\sinput',main.last_response ) :             
            main.log.warn("Incomplete\sinput"+main.last_response)
            return main.FALSE
        else:
            main.log.info("Successfully added Openflow Controller")
            return main.TRUE
        
        
    def create_openflow_instance(self,**instanceargs):
        for key in instanceargs:
           vars(self)[key] = instanceargs[key]
        
        if not self.openflow_mode():
            return main.FALSE
        
        if self.instance_name :
            self.execute(cmd='instance '+self.instance_name, prompt = '\(of-inst-'+self.instance_name+'\)',timeout = 3)
            
            if re.search('\(of-inst-'+self.instance_name+'\)', main.last_response):
                main.log.info("Configuring Openflow instance "+self.instance_name)
            else : 
                main.log.warn("Fail to configure Openflow instance"+self.instance_name+"\n\n"+main.last_response)
                return main.FALSE
        if self.controller_id :
            self.execute(cmd='controller-id '+self.controller_id, prompt = '\(of-inst-'+self.instance_name+'\)',timeout = 3)
            main.log.info(main.last_response)
        
        if self.member :
            self.execute(cmd='member vlan '+self.member_vlan_id, prompt = '\(of-inst-'+self.instance_name+'\)',timeout = 3)
            main.log.info(main.last_response)
    
        if self.execute(cmd='enable', prompt = '\(of-inst-'+self.instance_name+'\)',timeout = 3):
            return main.TRUE
        else :
            return main.FALSE
    
    def pair_vlan_with_openflow_instance(self,vlan_id):
        self.configure()
        self.execute(cmd='vlan '+vlan_id, prompt = '\(vlan-'+vlan_id+'\)',timeout = 3)
        if re.search('\(vlan-'+vlan_id+'\)', main.last_response):
            main.log.info("Configuring VLAN "+vlan_id)
        else : 
            main.log.warn("Fail to configure Vlan"+self.vlan_id+main.last_response)
            return main.FALSE
        
        self.execute(cmd='openflow enable', prompt = '\(vlan-'+vlan_id+'\)',timeout = 3)
        if re.search('\(vlan-'+vlan_id+'\)', main.last_response):
            main.log.info("Configuring VLAN "+vlan_id)
        else : 
            main.log.warn("Fail to configure Vlan"+self.vlan_id+main.last_response)
            return main.FALSE
        
    def show_openflow_instance(self,instance_name):
        
        self.execute(cmd='show openflow instance '+instance_name, prompt = '#',timeout = 3)
        return main.TRUE
    
    def show(self, command):
        self.execute(cmd=command, prompt = '#',timeout = 3)
        return main.TRUE
    
    
    def openflow_enable(self):
        self.configure()
        self.execute(cmd='openflow enable', prompt = '#',timeout = 3)
        return main.TRUE
    
    def openflow_disable(self):
        self.configure()
        self.execute(cmd='openflow enable', prompt = '#',timeout = 3)
        return main.TRUE
    
    def remove_controller(self,controller_id):
        self.configure()
        self.execute(cmd='no controller-id '+controller_id, prompt = '#',timeout = 3)
        return main.TRUE
    
    def remove_vlan(self,vlan_id):
        self.configure()
        if self.execute(cmd='no vlan '+vlan_id, prompt = '#',timeout = 3):
            return main.TRUE
        else :
            self.execute(cmd=' '+vlan_id, prompt = '#',timeout = 3)
            return main.TRUE
    
    def remove_openflow_instance(self,instance_name):
        self.configure()
        self.execute(cmd='no openflow instance '+instance_name, prompt = '#',timeout = 3)
        return main.TRUE
