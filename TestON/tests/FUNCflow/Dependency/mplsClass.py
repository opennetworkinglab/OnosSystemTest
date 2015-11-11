import scapy

class MPLS(Packet):
        name = "MPLS"
        fields_desc =  [
                BitField("label", 3, 20),
                BitField("experimental_bits", 0, 3),
                BitField("bottom_of_label_stack", 1, 1), # Now we're at the bottom
                ByteField("TTL", 255)
        ]
