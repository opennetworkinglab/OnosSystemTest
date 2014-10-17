#!/usr/bin/env python

'''
This driver interacts with ONOS bench, the OSGi platform 
that configures the ONOS nodes. (aka ONOS-next) 

Please follow the coding style demonstrated by existing 
functions and document properly.

If you are a contributor to the driver, please
list your email here for future contact:

jhall@onlab.us
andrew@onlab.us

OCT 9 2014

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

class OnosDriver(CLI):

    def __init__(self):
        '''
        Initialize client 
        '''
        super(CLI, self).__init__()

    def connect(self,**connectargs):
        '''
        Creates ssh handle for ONOS "bench".
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
            self.handle = super(OnosDriver,self).connect(
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
            self.handle.sendline("exit")
            self.handle.expect("closed")
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
        except:
            main.log.error(self.name + ": Connection failed to the host")
            response = main.FALSE
        return response

    def onos_package(self):
        '''
        Produce a self-contained tar.gz file that can be deployed
        and executed on any platform with Java 7 JRE. 
        '''
        
        try:
            self.handle.sendline("onos-package")
            self.handle.expect("onos-package")
            self.handle.expect("tar.gz",timeout=10)
            handle = str(self.handle.before)
            main.log.info("onos-package command returned: "+
                    handle)
            #As long as the sendline does not time out, 
            #return true. However, be careful to interpret
            #the results of the onos-package command return
            return main.TRUE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":    " + self.handle.before)
        except:
            main.log.error("Failed to package ONOS")
            main.cleanup()
            main.exit()

    def clean_install(self):
        '''
        Runs mvn clean install in the root of the ONOS directory. 
        This will clean all ONOS artifacts then compile each module 

        Returns: main.TRUE on success 
        On Failure, exits the test
        '''
        try:
            main.log.info("Running 'mvn clean install' on " + str(self.name) + 
                    ". This may take some time.") 
            self.handle.sendline("cd "+ self.home)
            self.handle.expect("\$")

            self.handle.sendline("\n")
            self.handle.expect("\$")
            self.handle.sendline("mvn clean install")
            self.handle.expect("mvn clean install")
            while 1:
                i=self.handle.expect([
                    'There\sis\sinsufficient\smemory\sfor\sthe\sJava\s\
                            Runtime\sEnvironment\sto\scontinue',
                    'BUILD\sFAILURE',
                    'BUILD\sSUCCESS',
                    'ONOS\$',
                    pexpect.TIMEOUT],timeout=600)
                if i == 0:
                    main.log.error(self.name + ":There is insufficient memory \
                            for the Java Runtime Environment to continue.")
                    #return main.FALSE
                    main.cleanup()
                    main.exit()
                if i == 1:
                    main.log.error(self.name + ": Build failure!")
                    #return main.FALSE
                    main.cleanup()
                    main.exit()
                elif i == 2:
                    main.log.info(self.name + ": Build success!")
                elif i == 3:
                    main.log.info(self.name + ": Build complete")
                    #Print the build time
                    for line in self.handle.before.splitlines():
                        if "Total time:" in line:
                            main.log.info(line)
                    self.handle.sendline("\n")
                    self.handle.expect("\$", timeout=60)
                    return main.TRUE
                elif i == 4:
                    main.log.error(self.name + ": mvn clean install TIMEOUT!")
                    #return main.FALSE
                    main.cleanup()
                    main.exit()
                else:
                    main.log.error(self.name + ": unexpected response from \
                            mvn clean install")
                    #return main.FALSE
                    main.cleanup()
                    main.exit()
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

    def git_pull(self, comp1=""):
        '''
        Assumes that "git pull" works without login
        
        This function will perform a git pull on the ONOS instance.
        If used as git_pull("NODE") it will do git pull + NODE. This is
        for the purpose of pulling from other nodes if necessary.

        Otherwise, this function will perform a git pull in the 
        ONOS repository. If it has any problems, it will return main.ERROR
        If it successfully does a git_pull, it will return a 1.
        If it has no updates, it will return a 0.

        '''
        try:
            # main.log.info(self.name + ": Stopping ONOS")
            #self.stop()
            self.handle.sendline("cd " + self.home)
            self.handle.expect("ONOS\$")
            if comp1=="":
                self.handle.sendline("git pull")
            else:
                self.handle.sendline("git pull " + comp1)
           
            uptodate = 0
            i=self.handle.expect(['fatal',
                'Username\sfor\s(.*):\s',
                '\sfile(s*) changed,\s',
                'Already up-to-date',
                'Aborting',
                'You\sare\snot\scurrently\son\sa\sbranch', 
                'You\sasked\sme\sto\spull\swithout\stelling\sme\swhich\sbranch\syou',
                'Pull\sis\snot\spossible\sbecause\syou\shave\sunmerged\sfiles',
                pexpect.TIMEOUT],
                timeout=300)
            #debug
           #main.log.report(self.name +": \n"+"git pull response: " + str(self.handle.before) + str(self.handle.after))
            if i==0:
                main.log.error(self.name + ": Git pull had some issue...")
                return main.ERROR
            elif i==1:
                main.log.error(self.name + ": Git Pull Asking for username. ")
                return main.ERROR
            elif i==2:
                main.log.info(self.name + ": Git Pull - pulling repository now")
                self.handle.expect("ONOS\$", 120)
                return main.TRUE
            elif i==3:
                main.log.info(self.name + ": Git Pull - Already up to date")
                return main.TRUE
            elif i==4:
                main.log.info(self.name + ": Git Pull - Aborting... Are there conflicting git files?")
                return main.ERROR
            elif i==5:
                main.log.info(self.name + ": Git Pull - You are not currently on a branch so git pull failed!")
                return main.ERROR
            elif i==6:
                main.log.info(self.name + ": Git Pull - You have not configured an upstream branch to pull from. Git pull failed!")
                return main.ERROR
            elif i==7:
                main.log.info(self.name + ": Git Pull - Pull is not possible because you have unmerged files.")
                return main.ERROR
            elif i==8:
                main.log.error(self.name + ": Git Pull - TIMEOUT")
                main.log.error(self.name + " Response was: " + str(self.handle.before))
                return main.ERROR
            else:
                main.log.error(self.name + ": Git Pull - Unexpected response, check for pull errors")
                return main.ERROR
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

    def git_checkout(self, branch="master"):
        '''
        Assumes that "git pull" works without login
        
        This function will perform a git git checkout on the ONOS instance.
        If used as git_checkout("branch") it will do git checkout of the "branch".

        Otherwise, this function will perform a git checkout of the master
        branch of the ONOS repository. If it has any problems, it will return 
        main.ERROR. 
        If the branch was already the specified branch, or the git checkout was 
        successful then the function will return main.TRUE.

        '''
        try:
            # main.log.info(self.name + ": Stopping ONOS")
            #self.stop()
            self.handle.sendline("cd " + self.home)
            self.handle.expect("ONOS\$")
            if branch != 'master':
                #self.handle.sendline('git stash')
                #self.handle.expect('ONOS\$')
                #print "After issuing git stash cmnd: ", self.handle.before
                cmd = "git checkout "+branch
                print "checkout cmd = ", cmd
                self.handle.sendline(cmd)
                uptodate = 0
                i=self.handle.expect(['fatal',
                    'Username\sfor\s(.*):\s',
                    'Already\son\s\'',
                    'Switched\sto\sbranch\s\'', 
                    pexpect.TIMEOUT],timeout=60)
            else:
                #self.handle.sendline('git stash apply')
                #self.handle.expect('ONOS\$')
                #print "After issuing git stash apply cmnd: ", self.handle.before
                cmd = "git checkout "+branch
                print "checkout cmd = ", cmd
                self.handle.sendline(cmd)
                uptodate = 0
                switchedToMaster = 0
                i=self.handle.expect(['fatal',
                    'Username\sfor\s(.*):\s',
                    'Already\son\s\'master\'',
                    'Switched\sto\sbranch\s\'master\'', 
                    pexpect.TIMEOUT],timeout=60)
 

            if i==0:
                main.log.error(self.name + ": Git checkout had some issue...")
                return main.ERROR
            elif i==1:
                main.log.error(self.name + ": Git checkout Asking for username!!! Bad!")
                return main.ERROR
            elif i==2:
                main.log.info(self.name + ": Git Checkout %s : Already on this branch" %branch)
                self.handle.expect("ONOS\$")
                print "after checkout cmd = ", self.handle.before
                switchedToMaster = 1
                return main.TRUE
            elif i==3:
                main.log.info(self.name + ": Git checkout %s - Switched to this branch" %branch)
                self.handle.expect("ONOS\$")
                print "after checkout cmd = ", self.handle.before
                switchedToMaster = 1
                return main.TRUE
            elif i==4:
                main.log.error(self.name + ": Git Checkout- TIMEOUT")
                main.log.error(self.name + " Response was: " + str(self.handle.before))
                return main.ERROR
            else:
                main.log.error(self.name + ": Git Checkout - Unexpected response, check for pull errors")
                return main.ERROR

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

    def get_version(self):
        '''
        Writes the COMMIT number to the report to be parsed by Jenkins data collecter.
        '''
        try:
            self.handle.sendline("export TERM=xterm-256color")
            self.handle.expect("xterm-256color")
            self.handle.expect("\$")
            self.handle.sendline("cd " + self.home + "; git log -1 --pretty=fuller --decorate=short | grep -A 5 \"commit\" --color=never; cd \.\.")
            self.handle.expect("cd ..")
            self.handle.expect("\$")
            response=(self.name +": \n"+ str(self.handle.before + self.handle.after))
            lines=response.splitlines()
            for line in lines:
                print line
            return lines[2]
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

    def create_cell_file(self, bench_ip, file_name, mn_ip_addrs,
            extra_feature_string, *onos_ip_addrs):
        '''
        Creates a cell file based on arguments
        Required:
            * Bench IP address (bench_ip)
                - Needed to copy the cell file over
            * File name of the cell file (file_name)
            * Mininet IP address (mn_ip_addrs)
                - Note that only 1 ip address is 
                  supported currently
            * ONOS IP addresses (onos_ip_addrs) 
                - Must be passed in as last arguments
        
        NOTE: Assumes cells are located at:
            ~/<self.home>/tools/test/cells/
        '''
        
        #Variable initialization
        cell_directory = self.home + "/tools/test/cells/"
        #We want to create the cell file in the dependencies directory
        #of TestON first, then copy over to ONOS bench
        temp_directory = "/tmp/"
        #Create the cell file in the directory for writing (w+)
        cell_file = open(temp_directory+file_name , 'w+')
        
        #Feature string is hardcoded environment variables
        #That you may wish to use by default on startup.
        #Note that you  may not want certain features listed
        #on here.
        core_feature_string = "export ONOS_FEATURES=webconsole,onos-api,"+\
                "onos-cli,onos-openflow,onos-app-mobility,onos-app-tvue,"+\
                "onos-app-proxyarp,"+extra_feature_string
        mn_string = "export OCN="
        onos_string = "export OC"
        temp_count = 1
   
        #Create ONOS_NIC ip address prefix
        temp_onos_ip = onos_ip_addrs[0] 
        temp_list = []
        temp_list = temp_onos_ip.split(".")
        #Omit last element of list to format for NIC
        temp_list = temp_list[:-1]
        #Structure the nic string ip
        nic_addr = ".".join(temp_list) + ".*\n"
        onos_nic_string = "export ONOS_NIC="+nic_addr

        try:
            #Start writing to file
            cell_file.write(core_feature_string + "\n")
            cell_file.write(onos_nic_string) 
            cell_file.write(mn_string +"'"+ mn_ip_addrs +"'"+ "\n") 

            for arg in onos_ip_addrs:
                #For each argument in onos_ip_addrs, write to file
                #Output should look like the following:
                #   export OC1='10.128.20.11'
                #   export OC2='10.128.20.12'
                cell_file.write(onos_string + str(temp_count) +
                        "=" + "'" + arg + "'" + "\n" )
                temp_count = temp_count + 1
            
            cell_file.close()

            #We use os.system to send the command to TestON cluster
            #to account for the case in which TestON is not located
            #on the same cluster as the ONOS bench
            #Note that even if TestON is located on the same cluster
            #as ONOS bench, you must setup passwordless ssh
            #between TestON and ONOS bench in order to automate the test.
            os.system("scp "+temp_directory+file_name+
                    " admin@"+bench_ip+":"+cell_directory)

            return main.TRUE

        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::")
            main.cleanup()
            main.exit()

    def set_cell(self, cellname):
        '''
        Calls 'cell <name>' to set the environment variables on ONOSbench
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

    def verify_cell(self):
        '''
        Calls 'onos-verify-cell' to check for cell installation
        '''
        #TODO: Add meaningful expect value

        try:
            #Clean handle by sending empty and expecting $
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline("onos-verify-cell")
            self.handle.expect("\$")
            handle_before = self.handle.before
            handle_after = self.handle.after
            #Get the rest of the handle
            self.handle.sendline("")
            self.handle.expect("\$")
            handle_more = self.handle.before

            main.log.info("Verify cell returned: "+handle_before+
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

    def onos_cli(self, ONOS_ip, cmdstr):
        '''
        Uses 'onos' command to send various ONOS CLI arguments.
        Required:
            * ONOS_ip: specify the ip of the cell machine
            * cmdstr: specify the command string to send
        
        This function is intended to expose the entire karaf 
        CLI commands for ONOS. Try to use this function first
        before attempting to write a ONOS CLI specific driver
        function. 
        You can see a list of available 'cmdstr' arguments 
        by starting onos, and typing in 'onos' to enter the
        onos> CLI. Then, type 'help' to see the list of
        available commands. 
        '''
        try:
            if not ONOS_ip:
                main.log.error("You must specify the IP address")
                return main.FALSE
            if not cmdstr:
                main.log.error("You must specify the command string")
                return main.FALSE

            cmdstr = str(cmdstr)
            self.handle.sendline("")
            self.handle.expect("\$")

            self.handle.sendline("onos -w " + ONOS_ip + " " + cmdstr)
            self.handle.expect("\$")

            handle_before = str(self.handle.before)
            handle_after = str(self.handle.after)
            
            self.handle.sendline("")
            self.handle.expect("\$")
            handle_more = str(self.handle.before)

            main.log.info("Command sent successfully")

            #Obtain return handle that consists of result from 
            #the onos command. The string may need to be 
            #configured further. 
            return_string = handle_before + handle_after + handle_more
            return return_string

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

    def onos_install(self, options="-f", node = ""):
        '''
        Installs ONOS bits on the designated cell machine.
        If -f option is provided, it also forces an uninstall. 
        Presently, install also includes onos-push-bits and 
        onos-config within.
        The node option allows you to selectively only push the jar 
        files to certain onos nodes

        Returns: main.TRUE on success and main.FALSE on failure
        '''
        try:
            self.handle.sendline("onos-install " + options + " " + node)
            self.handle.expect("onos-install ")
            #NOTE: this timeout may need to change depending on the network and size of ONOS
            i=self.handle.expect(["Network\sis\sunreachable",
                "onos\sstart/running,\sprocess",
                pexpect.TIMEOUT],timeout=60)


            if i == 0:
                main.log.warn("Network is unreachable")
                return main.FALSE
            elif i == 1:
                main.log.info("ONOS was installed on the VM and started")
                return main.TRUE
            elif i == 2: 
                main.log.info("Installation of ONOS on the VM timed out")
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

    def onos_start(self, node_ip):
        '''
        Calls onos command: 'onos-service [<node-ip>] start'
        This command is a remote management of the ONOS upstart daemon
        '''

        try:
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline("onos-service "+str(node_ip)+
                " start")
            i = self.handle.expect([
                "Job\sis\salready\srunning",
                "start/running",
                "Unknown\sinstance",
                pexpect.TIMEOUT],timeout=60)

            if i == 0:
                main.log.info("Service is already running")
                return main.TRUE
            elif i == 1:
                main.log.info("ONOS service started")
                return main.TRUE
            else:
                main.log.error("ONOS service failed to start")
                main.cleanup()
                main.exit()
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

    def onos_stop(self, node_ip):
        '''
        Calls onos command: 'onos-service [<node-ip>] stop'
        This command is a remote management of the ONOS upstart daemon
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline("onos-service "+str(node_ip)+
                " stop")
            i = self.handle.expect([
                "stop/waiting",
                "Unknown\sinstance",
                pexpect.TIMEOUT],timeout=60)

            if i == 0:
                main.log.info("ONOS service stopped")
                return main.TRUE
            elif i == 1:
                main.log.info("Unknown ONOS instance specified: "+
                        str(node_ip))
                return main.FALSE
            else:
                main.log.error("ONOS service failed to stop")
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

    def onos_uninstall(self):
        '''
        Calls the command: 'onos-uninstall'
        Uninstalls ONOS from the designated cell machine, stopping 
        if needed
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline("onos-uninstall")
            self.handle.expect("\$")

            main.log.info("ONOS cell machine was uninstalled")
            #onos-uninstall command does not return any text
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

    def onos_kill(self, node_ip):
        '''
        Calls the command: 'onos-kill [<node-ip>]'
        "Remotely, and unceremoniously kills the ONOS instance running on
        the specified cell machine" - Tom V
        '''
        
        try:
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline("onos-kill " + str(node_ip))
            i = self.handle.expect([
                "\$",
                "No\sroute\sto\shost",
                "password:",
                pexpect.TIMEOUT], timeout=20)
            
            if i == 0:
                main.log.info("ONOS instance "+str(node_ip)+" was killed")
                return main.TRUE
            elif i == 1:
                main.log.info("No route to host")
                return main.FALSE
            elif i == 2:
                main.log.info("Passwordless login for host: "+str(node_ip)+
                        " not configured")
                return main.FALSE
            else:
                main.log.info("ONOS instasnce was not killed")
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

    def onos_start_network(self, mntopo):
        '''
        Calls the command 'onos-start-network [<mininet-topo>]
        "remotely starts the specified topology on the cell's 
        mininet machine against all controllers configured in the
        cell." 
        * Specify mininet topology file name for mntopo
        * Topo files should be placed at:
          ~/<your-onos-directory>/tools/test/topos
        
        NOTE: This function will take you to the mininet prompt
        '''
        try:
            if not mntopo:
                main.log.error("You must specify a topo file to execute")
                return main.FALSE
            
            mntopo = str(mntopo)
            self.handle.sendline("")
            self.handle.expect("\$")

            self.handle.sendline("onos-start-network " + mntopo)
            self.handle.expect("mininet>")
            main.log.info("Network started, entered mininet prompt")

            #TODO: Think about whether return is necessary or not

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


    def isup(self, node = ""):
        '''
        Run's onos-wait-for-start which only returns once ONOS is at run 
        level 100(ready for use)

        Returns: main.TRUE if ONOS is running and main.FALSE on timeout
        '''
        try:
            self.handle.sendline("onos-wait-for-start " + node )
            self.handle.expect("onos-wait-for-start")
            #NOTE: this timeout is arbitrary"
            i = self.handle.expect(["\$", pexpect.TIMEOUT], timeout = 120)
            if i == 0:
                main.log.info(self.name + ": " + node + " is up")
                return main.TRUE
            elif i == 1:
                #NOTE: since this function won't return until ONOS is ready,
                #   we will kill it on timeout
                self.handle.sendline("\003")    #Control-C
                self.handle.expect("\$")
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


    def get_topology(self, ip):
        '''
        parses the onos:topology output
        Returns: a topology dict populated by the key values found in 
                 the cli command.
        '''

        try:
            #call the cli to get the topology summary
            cmdstr = "onos:topology"
            cli_result = self.onos_cli(ip, cmdstr)


            #Parse the output
            topology = {}
            #for line in cli_result.split("\n"):
            for line in cli_result.splitlines():
                if not line.startswith("time="):
                    continue
                #else
                print line
                for var in line.split(","):
                    print "'"+var+"'"
                    print "'"+var.strip()+"'"
                    key, value = var.strip().split("=")
                    topology[key] = value
            print topology
            devices = topology.get('devices', False)
            print devices
            links = topology.get('links', False)
            print links
            clusters = topology.get('clusters', False)
            print clusters
            paths = topology.get('paths', False)
            print paths

            return topology
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

    def tshark_grep(self, grep, directory, interface='eth0'):
        '''
        Required:
            * grep string 
            * directory to store results
        Optional:
            * interface - default: eth0
        Description:
            Uses tshark command to grep specific group of packets
            and stores the results to specified directory.
            The timestamp is hardcoded to be in epoch 
        '''
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("\r")
        self.handle.sendline("tshark -i "+str(interface)+
                " -t e | grep \""+str(grep)+"\" > "+directory+" &")
        self.handle.sendline("\r")
        self.handle.expect("Capturing on")
        self.handle.sendline("\r")
        self.handle.expect("\$")

    def tshark_stop(self):
        '''
        Removes wireshark files from /tmp and kills all tshark processes
        '''
        self.execute(cmd="rm /tmp/wireshark*")
        self.handle.sendline("")
        self.handle.sendline("sudo kill -9 `ps -ef | grep \"tshark -i\" |"+
                " grep -v grep | awk '{print $2}'`")
        self.handle.sendline("")
        main.log.info("Tshark stopped")











