from scapy.contrib.gtp import GTP_U_Header, GTPPDUSessionContainer
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
import codecs

UDP_GTP_PORT = 2152
DEFAULT_GTP_TUNNEL_SPORT = 1234  # arbitrary, but different from 2152

IP_HDR_BYTES = 20
UDP_HDR_BYTES = 8
GTPU_HDR_BYTES = 8
GTPU_OPTIONS_HDR_BYTES = 4
GTPU_EXT_PSC_BYTES = 4


def simple_gtp_udp_packet(
        eth_dst=None,
        eth_src=None,
        ip_src="192.168.0.1",
        ip_dst="192.168.0.2",
        s1u_addr="100.0.0.1",
        enb_addr="192.168.101.1",
        ip_ttl=64,
        gtp_teid=0xFF,  # dummy teid
        pktlen=136,
        ext_psc_type=None,
        ext_psc_qfi=0,
):
    pktlen = pktlen - IP_HDR_BYTES - UDP_HDR_BYTES - GTPU_HDR_BYTES
    if ext_psc_type is not None:
        pktlen = pktlen - GTPU_OPTIONS_HDR_BYTES - GTPU_EXT_PSC_BYTES
    pkt = simple_udp_packet(eth_src=eth_src, eth_dst=eth_dst, ip_src=ip_src,
                            ip_dst=ip_dst, pktlen=pktlen)
    gtp_pkt = pkt_add_gtp(
        pkt,
        out_ipv4_src=enb_addr,
        out_ipv4_dst=s1u_addr,
        teid=gtp_teid,
        ext_psc_type=ext_psc_type,
        ext_psc_qfi=ext_psc_qfi,
    )
    gtp_pkt[Ether].src = eth_src
    gtp_pkt[Ether].dst = eth_dst
    gtp_pkt[IP].ttl = ip_ttl
    return gtp_pkt


def pkt_add_gtp(
        pkt,
        out_ipv4_src,
        out_ipv4_dst,
        teid,
        sport=DEFAULT_GTP_TUNNEL_SPORT,
        dport=UDP_GTP_PORT,
        ext_psc_type=None,
        ext_psc_qfi=None,
):
    gtp_pkt = (
            Ether(src=pkt[Ether].src, dst=pkt[Ether].dst)
            / IP(src=out_ipv4_src, dst=out_ipv4_dst, tos=0, id=0x1513, flags=0,
                 frag=0, )
            / UDP(sport=sport, dport=dport, chksum=0)
            / GTP_U_Header(gtp_type=255, teid=teid)
    )
    if ext_psc_type is not None:
        # Add QoS Flow Identifier (QFI) as an extension header (required for 5G RAN)
        gtp_pkt = gtp_pkt / GTPPDUSessionContainer(type=ext_psc_type,
                                                   QFI=ext_psc_qfi)
    return gtp_pkt / pkt[Ether].payload


# Simplified version of simple_udp_packet from https://github.com/p4lang/ptf/blob/master/src/ptf/testutils.py
def simple_udp_packet(
        pktlen=100,
        eth_dst="00:01:02:03:04:05",
        eth_src="00:06:07:08:09:0a",
        ip_src="192.168.0.1",
        ip_dst="192.168.0.2",
        udp_sport=1234,
        udp_dport=80,
        udp_payload=None,
):
    pkt = Ether(src=eth_src, dst=eth_dst) / IP(src=ip_src, dst=ip_dst) / UDP(
        sport=udp_sport, dport=udp_dport)
    if udp_payload:
        pkt = pkt / udp_payload
    return pkt / codecs.decode(
        "".join(["%02x" % (x % 256) for x in range(pktlen - len(pkt))]), "hex")
