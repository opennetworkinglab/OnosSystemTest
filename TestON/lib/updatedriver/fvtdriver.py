class driver :
    def __init__(self):
        self.default = ''


    def runTest(self,self) :
        return TemplateTest.runTest(self)

    def tearDown(self,self) :
        return TemplateTest.tearDown(self)

    def setUp(self,self) :
        return TemplateTest.setUp(self)

    def chkSetUpCondition(self,self,fv,sv_ret,ctl_ret,sw_ret) :
        return TemplateTest.chkSetUpCondition(self,fv,sv_ret,ctl_ret,sw_ret)

    def ofmsgSndCmpWithXid(self,parent,snd_list,exp_list,xid_ignore,hdr_only) :
        return testutils.ofmsgSndCmpWithXid(parent,snd_list,exp_list,xid_ignore,hdr_only)

    def genPacketOut(self,parent,xid,buffer_id,in_port,action_ports,pkt) :
        return testutils.genPacketOut(parent,xid,buffer_id,in_port,action_ports,pkt)

    def spawnApiClient(self,parent,user,pswd,rpcport) :
        return testutils.spawnApiClient(parent,user,pswd,rpcport)

    def genPhyPort(self,name,addr,port_no) :
        return testutils.genPhyPort(name,addr,port_no)

    def tearDownFlowVisor(self,parent) :
        return testutils.tearDownFlowVisor(parent)

    def _ruleLenChecker(self,parent,rule,exp_len) :
        return testutils._ruleLenChecker(parent,rule,exp_len)

    def genPacketIn(self,xid,buffer_id,in_port,pkt) :
        return testutils.genPacketIn(xid,buffer_id,in_port,pkt)

    def chkSliceStats(self,parent,controller_number,ofproto,exp_snd_count,exp_rcv_count) :
        return testutils.chkSliceStats(parent,controller_number,ofproto,exp_snd_count,exp_rcv_count)

    def spawnFlowVisor(self,parent,config_file,fv_cmd,fv_args) :
        return testutils.spawnFlowVisor(parent,config_file,fv_cmd,fv_args)

    def addController(self,parent,num) :
        return testutils.addController(parent,num)

    def genTrailer(self,controller_name,flowvisor_name) :
        return testutils.genTrailer(controller_name,flowvisor_name)

    def genVal32bit(self,) :
        return testutils.genVal32bit()

    def recvStats(self,parent,swId,typ) :
        return testutils.recvStats(parent,swId,typ)

    def simpleLldpPacket(self,dl_dst,dl_src,dl_type,lldp_chassis_id,lldp_port_id,lldp_ttl,trailer) :
        return testutils.simpleLldpPacket(dl_dst,dl_src,dl_type,lldp_chassis_id,lldp_port_id,lldp_ttl,trailer)

    def _tlvPack(self,tlv_type,tlv_value) :
        return testutils._tlvPack(tlv_type,tlv_value)

    def ofmsgSndCmp(self,parent,snd_list,exp_list,xid_ignore,hdr_only) :
        return testutils.ofmsgSndCmp(parent,snd_list,exp_list,xid_ignore,hdr_only)

    def _b2a(self,str) :
        return testutils._b2a(str)

    def simplePacket(self,pktlen,dl_dst,dl_src,dl_vlan,dl_vlan_pcp,dl_vlan_cfi,dl_type,nw_src,nw_dst,nw_tos,nw_proto,tp_src,tp_dst) :
        return testutils.simplePacket(pktlen,dl_dst,dl_src,dl_vlan,dl_vlan_pcp,dl_vlan_cfi,dl_type,nw_src,nw_dst,nw_tos,nw_proto,tp_src,tp_dst)

    def setRule(self,parent,sv,rule,num_try) :
        return testutils.setRule(parent,sv,rule,num_try)

    def genFloModFromPkt(self,parent,pkt,ing_port,action_list,wildcards,egr_port) :
        return testutils.genFloModFromPkt(parent,pkt,ing_port,action_list,wildcards,egr_port)

    def addSwitch(self,parent,num,port,switch_features,nPorts) :
        return testutils.addSwitch(parent,num,port,switch_features,nPorts)

    def test_param_get(self,config,key,default) :
        return testutils.test_param_get(config,key,default)

    def setUpTestEnv(self,parent,config_file,fv_cmd,num_of_switches,num_of_controllers,rules) :
        return testutils.setUpTestEnv(parent,config_file,fv_cmd,num_of_switches,num_of_controllers,rules)

    def _hdrParse(self,pkt) :
        return testutils._hdrParse(pkt)

    def _pktParse(self,pkt) :
        return testutils._pktParse(pkt)

    def _a2b(self,str) :
        return testutils._a2b(str)

    def genFeaturesReply(self,dpid,ports,xid) :
        return testutils.genFeaturesReply(dpid,ports,xid)

    def chkFlowdb(self,parent,controller_number,switch_number,exp_count,exp_rewrites) :
        return testutils.chkFlowdb(parent,controller_number,switch_number,exp_count,exp_rewrites)

    def genFlowModFlush(self,) :
        return testutils.genFlowModFlush()
