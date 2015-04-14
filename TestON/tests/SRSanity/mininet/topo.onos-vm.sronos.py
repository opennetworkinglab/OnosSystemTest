"""
This is sample config file for start_topo.py.
Please rename to topo.`hostname`.py before use.
"""
def createTopo():
  return {
    "controllers": {
        "sronos01" : "10.128.4.55:6633",
        "sronos02" : "10.128.4.56:6633"
    },
    "switches": {
        # Note that dpid is optional.
        # If omitted, sequential number will be assigned.
        "s1": {"controllers": [ "sronos01", "sronos02" ] },
        "s2": {"controllers": [ "sronos02", "sronos01" ] },
        "s3": {"controllers": [ "sronos01", "sronos02" ] },
        "s4": {"controllers": [ "sronos02", "sronos01" ] },
        "s5": {"controllers": [ "sronos01", "sronos02" ] },
        "s6": {"controllers": [ "sronos02", "sronos01" ] },
    },
    "hosts": {
        # Only default interface is configurable for now.
        # mac and ip are optional and automatically assigned if omitted.
        # To avoid collision of address, do not mix specified hosts and omitted hosts.
        "h1": { "mac": "00:00:00:00:01:01", "ip": "10.0.1.1" },
        "h2": { "mac": "00:00:00:00:02:02", "ip": "7.7.7.7" },
#         "h01": {},
#         "h02": {},
#         "h03": {},
#         "h04": {},
#         "h05": {}
    },
    "links": [
        # Note that multiple links between nodes are unsupported (if declared, single link will be created).
        {
            "node1": "h1",
            "node2": "s1"
        },{
            "node1": "h2",
            "node2": "s6"
        },
	{
            "node1": "s1",
            "node2": "s2"
        },{
            "node1": "s1",
            "node2": "s3"
        },
        {
            "node1": "s2",
            "node2": "s3"
        },{
            "node1": "s2",
            "node2": "s5"
        },
        {
            "node1": "s3",
            "node2": "s4"
        },{
            "node1": "s4",
            "node2": "s5"
        },
        {
            "node1": "s4",
            "node2": "s6"
        },{
            "node1": "s5",
            "node2": "s6"
        }
    ]
}
