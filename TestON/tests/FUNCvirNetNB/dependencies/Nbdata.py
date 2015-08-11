"""
This file provide the data
lanqinglong@huawei.com
"""
import json

class NetworkData:

    def __init__(self):
        self.id = ''
        self.state = 'ACTIVE'
        self.name = 'onosfw-1'
        self.physicalNetwork = 'none'
        self.admin_state_up = 'true'
        self.tenant_id = ''
        self.routerExternal = 'false'
        self.type ='LOCAL'
        self.segmentationID = '6'
        self.shared = 'false'

    def DictoJson(self):

        if self.id =='' or self.tenant_id == '':
            print 'Id and tenant id is necessary!'

        Dicdata = {}
        if self.id !='':
            Dicdata['id'] = self.id
        if self.state != '':
            Dicdata['status'] = self.state
        if self.name !='':
            Dicdata['name'] = self.name
        if self.physicalNetwork !='':
            Dicdata['provider:physical_network'] = self.physicalNetwork
        if self.admin_state_up !='':
            Dicdata['admin_state_up'] = self.admin_state_up
        if self.tenant_id !='':
            Dicdata['tenant_id'] = self.tenant_id
        if self.routerExternal !='':
            Dicdata['router:external'] = self.routerExternal
        if self.type !='':
            Dicdata['provider:network_type'] = self.type
        if self.segmentationID !='':
            Dicdata['provider:segmentation_id'] = self.segmentationID
        if self.shared !='':
            Dicdata['shared'] = self.shared

        Dicdata = {'network': Dicdata}

        return json.dumps(Dicdata,indent=4)

    def Ordered(self,obj):

        if isinstance(obj, dict):
            return sorted((k,self.Ordered(v)) for k,  v in obj.items())
        if isinstance(obj, list):
            return sorted(self.Ordered(x) for x in obj )
        else:
            return obj

    def JsonCompare(self,SourceData,DestiData,FirstPara,SecondPara):

        try:
            SourceCompareDataDic = json.loads(SourceData)
            DestiCompareDataDic = json.loads(DestiData)
        except ValueError:
            print "SourceData or DestData is not JSON Type!"
            return False

        Socom = SourceCompareDataDic[FirstPara][SecondPara]
        Decom = DestiCompareDataDic[FirstPara][SecondPara]
        if Socom == Decom:
            return True
        else:
            print "Source Compare data:"+FirstPara+"."+SecondPara+"="+Socom
            print "Dest Compare data: "+FirstPara+"."+SecondPara+"="+str(Decom)
            return False

class SubnetData(NetworkData):

    def __init__(self):
        self.id = ''
        self.tenant_id = ''
        self.network_id = ''
        self.nexthop = '192.168.1.1'
        self.destination = '192.168.1.1/24'
        self.start = '192.168.2.2'
        self.end = '192.168.2.254'
        self.ipv6_address_mode = 'DHCPV6_STATELESS'
        self.ipv6_ra_mode = 'DHCPV6_STATELESS'
        self.cidr = '192.168.1.1/24'
        self.enable_dhcp = 'true'
        self.dns_nameservers = 'aaa'
        self.gateway_ip = '192.168.2.1'
        self.ip_version = 'INET'
        self.shared = 'false'
        self.name = 'demo-subnet'

    def DictoJson(self):
        if self.id =='' or self.tenant_id == '':
            print 'Id and tenant id is necessary!'

        Dicdata = {}
        host_routesdata = []
        host_routesdata.append({'nexthop': self.nexthop,'destination': self.destination})
        allocation_pools = []
        allocation_pools.append({'start': self.start,'end':self.end})

        if self.id != '':
            Dicdata['id'] = self.id
        if self.network_id != '':
            Dicdata['network_id'] = self.network_id
        if self.name != '':
            Dicdata['name'] = self.name
        if self.nexthop != '':
            Dicdata['host_routes'] = host_routesdata
        if self.tenant_id != '':
            Dicdata['tenant_id'] = self.tenant_id
        if self.start != '':
            Dicdata['allocation_pools'] = allocation_pools
        if self.shared != '':
            Dicdata['shared'] = self.shared
        if self.ipv6_address_mode != '':
            Dicdata['ipv6_address_mode'] = self.ipv6_address_mode
        if self.ipv6_ra_mode != '':
            Dicdata['ipv6_ra_mode'] = self.ipv6_ra_mode
        if self.cidr != '':
            Dicdata['cidr'] = self.cidr
        if self.enable_dhcp != '':
            Dicdata['enable_dhcp'] = self.enable_dhcp
        if self.dns_nameservers != '':
            Dicdata['dns_nameservers'] = self.dns_nameservers
        if self.gateway_ip != '':
            Dicdata['gateway_ip'] = self.gateway_ip
        if self.ip_version != '':
            Dicdata['ip_version'] = self.ip_version

        Dicdata = {'subnet': Dicdata}

        return json.dumps(Dicdata,indent=4)

    def Ordered(self,obj):
        super(NetworkData,self).Ordered(obj)

    def JsonCompare(self,SourceData,DestiData,FirstPara,SecondPara):
        super(NetworkData,self).JsonCompare(SourceData,DestiData,FirstPara,SecondPara)

class VirtualPortData(NetworkData):

    def __init__(self):
        self.id = ''
        self.state = 'ACTIVE'
        self.bindingHostId = 'fa:16:3e:76:8e:88'
        self.allowedAddressPairs = [{'macAddress':'fa:16:3e:76:8e:88','ipAddress':'192.168.1.1'}]
        self.deviceOwner = 'none'
        self.fixedIp = []
        self.securityGroups = [{'securityGroup':'asd'}]
        self.adminStateUp = 'true'
        self.networkId = ''
        self.tenantId = ''
        self.subnetId = ''
        self.bindingvifDetails = 'port_filter'
        self.bindingvnicType = 'normal'
        self.bindingvifType = 'ovs'
        self.macAddress = 'fa:16:3e:76:8e:88'
        self.deviceId = 'a08aa'
        self.name = 'u'

    def DictoJson(self):
        if self.id == '' or self.tenant_id == ' ' or self.networkId == '':
            print 'Id/tenant id/networkid/subnetId is necessary!'

        Dicdata = {}
        fixedIp =[]
        fixedIp.append({'subnetId':self.subnetId,'ipAddress':'192.168.1.4'})
        allocation_pools = []

        if self.id != '':
            Dicdata['id'] = self.id
        if self.state != '':
            Dicdata['state'] = self.state
        if self.bindingHostId != '':
            Dicdata['bindingHostId'] = self.bindingHostId
        if self.allowedAddressPairs != '':
            Dicdata['allowedAddressPairs'] = self.allowedAddressPairs
        if self.deviceOwner != '':
            Dicdata['deviceOwner'] = self.deviceOwner
        if self.fixedIp != []:
            Dicdata['fixedIp'] = fixedIp
        if self.securityGroups != '':
            Dicdata['securityGroups'] = self.securityGroups
        if self.adminStateUp != '':
            Dicdata['adminStateUp'] = self.adminStateUp
        if self.networkId != '':
            Dicdata['networkId'] = self.networkId
        if self.tenantId != '':
            Dicdata['tenantId'] = self.tenantId
        if self.subnetId != '':
            Dicdata['subnetId'] = self.subnetId
        if self.bindingvifDetails != '':
            Dicdata['bindingvifDetails'] = self.bindingvifDetails
        if self.bindingvnicType != '':
            Dicdata['bindingvnicType'] = self.bindingvnicType
        if self.bindingvifType != '':
            Dicdata['bindingvifType'] = self.bindingvifType
        if self.macAddress != '':
            Dicdata['macAddress'] = self.macAddress
        if self.deviceId != '':
            Dicdata['deviceId'] = self.deviceId
        if self.name != '':
            Dicdata['name'] = self.name

            Dicdata = {'virtualport': Dicdata}

            return json.dumps(Dicdata,indent=4)

    def Ordered(self,obj):
        super(NetworkData,self).Ordered(obj)

    def JsonCompare(self,SourceData,DestiData,FirstPara,SecondPara):
        super(NetworkData,self).JsonCompare(SourceData,DestiData,FirstPara,SecondPara)