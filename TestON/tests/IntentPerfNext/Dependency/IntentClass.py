
def __init__(self):
    self_ = self

def printLog(main):
    main.log.info("Print log success")

def iptablesDropAllNodes(main, MN_ip, sw_port):
    #INPUT RULES 
    main.ONOS1.handle.sendline(
        "sudo iptables -A INPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")
    main.ONOS2.handle.sendline(
        "sudo iptables -A INPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")
    main.ONOS3.handle.sendline(
        "sudo iptables -A INPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")
    main.ONOS4.handle.sendline(
        "sudo iptables -A INPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")
    main.ONOS5.handle.sendline(
        "sudo iptables -A INPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")
    main.ONOS6.handle.sendline(
        "sudo iptables -A INPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")
    main.ONOS7.handle.sendline(
        "sudo iptables -A INPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")

    main.ONOS1.handle.sendline(
        "sudo iptables -A OUTPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")
    main.ONOS2.handle.sendline(
        "sudo iptables -A OUTPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")
    main.ONOS3.handle.sendline(
        "sudo iptables -A OUTPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")
    main.ONOS4.handle.sendline(
        "sudo iptables -A OUTPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")
    main.ONOS5.handle.sendline(
        "sudo iptables -A OUTPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")
    main.ONOS6.handle.sendline(
        "sudo iptables -A OUTPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")
    main.ONOS7.handle.sendline(
        "sudo iptables -A OUTPUT -p tcp -s "+
        MN_ip+" --dport "+sw_port+" -j DROP")

def uninstallAllNodes(main, node_ip_list):
    for node in node_ip_list:
        main.ONOSbench.onos_uninstall(node_ip = node)
