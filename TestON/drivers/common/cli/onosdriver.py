#!/usr/bin/env python
'''
TODO: Document
'''


import time
import pexpect
import re
import traceback
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
            self.handle = super(OnosCliDriver,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd, home = self.home)

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
        import os.path
        
        try:
            self.handle.sendline("onos-package")
            self.handle.expect("\$")
            handle = str(self.handle.before)
            main.log.info("onos-package command returned: "+
                    handle)
          
            #Create list out of the handle by partitioning 
            #spaces. 
            #NOTE: The last element of the list at the time
            #      of writing this function is the filepath
            #save this filepath for comparison later on
            temp_list = handle.split(" ")
            file_path = handle[-1:]
           
            #If last string contains the filepath, return
            # as success. 
            if "/tmp" in file_path:
                return main.TRUE
            else:
                return main.FALSE

        except:
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
            self.handle.sendline("mvn clean install")
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
