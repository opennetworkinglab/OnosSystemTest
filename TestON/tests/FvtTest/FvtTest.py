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
class FvtTest :

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :

    
        main.case("Checking FVT")
        main.step("Checking the FVT")
        pkt = main.FVT.simplePacket("SRC_MAC_FOR_CTL0_0")
        in_port = 3
        msg = main.FVT.genPacketIn(in_port=in_port, pkt=pkt)
        snd_list = ["switch", 0, msg]
        exp_list = [["controller", 0, msg]]
        res = main.FVT.ofmsgSndCmp(snd_list , exp_list , xid_ignore=True, hdr_only=True)
        utilities.assert_equals(expect=True,actual=res,onpass="Received expected message",onfail="Received unexpected message")
    
        #Packet_in for controller1
        pkt = main.FVT.simplePacket("SRC_MAC_FOR_CTL1_0")
        in_port = 3
        msg = main.FVT.genPacketIn(in_port=in_port, pkt=pkt)
        snd_list = ["switch", 0, msg]
        exp_list = [["controller", 1, msg]]
        res = main.FVT.ofmsgSndCmp(snd_list , exp_list , xid_ignore=True)
        utilities.assert_equals(expect=True,actual=res,onpass="Received expected message",onfail="Received unexpected message")
