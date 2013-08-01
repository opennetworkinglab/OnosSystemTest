'''
	
 *   TestON is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 2 of the License, or
 *   (at your option) any later version.

 *   TestON is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.


'''

class VyattaTest :

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :

        main.case("VyattaTest Sample Test")
        main.step("VyattaTest Sample Test")
        config_result = main.Vyatta.configure()
        main.log.info(config_result)
        
        command_details = main.Vyatta.get_details("show")
        main.log.info("show \n command_details\n\t"+ str(command_details))
        
        command_details = main.Vyatta.get_details("show interfaces")
        main.log.info("show interfaces \n command_details\n\t"+ str(command_details))
                
        command_details = main.Vyatta.get_details("show interfaces ethernet")
        main.log.info("show interfaces ethernet \n command_details\n\t"+ str(command_details))
                
        command_details = main.Vyatta.get_details("show interfaces ethernet eth1")
        main.log.info("show interfaces ethernet eth1 \n command_details\n\t"+ str(command_details))
        
        command_details = main.Vyatta.get_details("show interfaces ethernet eth1 address")
        main.log.info("show interfaces ethernet eth1 address \n command_details\n\t"+ str(command_details))
        
        
        '''
        main.Vyatta.handle.expect("\$")
        
        resultCommand = main.Vyatta.execute(cmd="configure",prompt='\#',timeout=10)
        
        resultCommand = main.Vyatta.execute(cmd="show interfaces ?",prompt='\#',timeout=10)
        
        print "Possible Options \t\t"
        print main.last_response
        print " ->"*10+"\n"*4
        import re
        match = re.findall("\n\s*.\s+(\w+)", main.last_response, 0)
        print match
        
        resultCommand = main.Vyatta.execute(cmd="XYZ",prompt='\#',timeout=10)
        
        print "Command result Upto here \t\t"
        print main.last_response
        print " ->"*10+"\n"*4
        import re
        match = re.findall("\n\s*.\s+(\w+)", main.last_response, 0)
        print match
        
        
        resultCommand = main.Vyatta.execute(cmd="XYZ",prompt='\#',timeout=10)
        
        print "Command result Upto here \t\t"
        print main.last_response
        print " ->"*10+"\n"*4
        import re
        match = re.findall("\n\s*.\s+(\w+)", main.last_response, 0)
        print match
        
        
        resultCommand = main.Vyatta.execute(cmd="show interfaces ethernet ?",prompt='\#',timeout=10)
        
        print "Possible Options \t\t"
        print main.last_response
        print " ->"*10+"\n"*4
        import re
        match = re.findall("\n\s*.\s+(\w+)", main.last_response, 0)
        print match
        
        resultCommand = main.Vyatta.execute(cmd="XYZ",prompt='\#',timeout=10)
        
        print "Command result Upto here \t\t"
        print main.last_response
        print " ->"*10+"\n"*4
        import re
        match = re.findall("\n\s*.\s+(\w+)", main.last_response, 0)
        print match
        '''
