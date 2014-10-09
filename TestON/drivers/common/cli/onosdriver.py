#!/usr/bin/env python
'''
'''
#TODO: Document

import sys
import time
import pexpect
import re
import traceback
import os.path
sys.path.append("../")
from drivers.common.clidriver import CLI

class OnosDriver(CLI):

    def __init__(self):
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
                #TODO: log the build time
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
                return 0
            elif i==3:
                main.log.info(self.name + ": Git Pull - Already up to date")
                return 1
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


    def isup(self, node = ""):
        '''
        Run's onos-wait-for-start which only returns once ONOS is at run level 100(ready for use)

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
