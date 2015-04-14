"""
This is sample config file for start_topo.py.
Please rename to topo.`hostname`.py before use.
"""
def createTopo():
  return {
    "controllers": {
        "onosdev1" : "192.168.56.11:6633",
        "onosdev2" : "192.168.56.12:6633"
    },
    "switches": {
        # Note that dpid is optional.
        # If omitted, sequential number will be assigned.
        "sw01": { "dpid": "0000000000000101", "controllers": [ "onosdev1" ] },
        "sw02": { "dpid": "0000000000000102", "controllers": [ "onosdev1" ] },
        "sw03": { "dpid": "0000000000000103", "controllers": [ "onosdev1" ] },
        "sw04": { "dpid": "0000000000000104", "controllers": [ "onosdev2" ] },
        "sw05": { "dpid": "0000000000000105", "controllers": [ "onosdev2", "onosdev1" ] }
    },
    "hosts": {
        # Only default interface is configurable for now.
        # mac and ip are optional and automatically assigned if omitted.
        # To avoid collision of address, do not mix specified hosts and omitted hosts.
        "h01": { "mac": "00:00:00:00:01:01", "ip": "10.0.0.1" },
        "h02": { "mac": "00:00:00:00:02:02", "ip": "10.0.0.2" },
        "h03": { "mac": "00:00:00:00:03:03", "ip": "10.0.0.3" },
        "h04": { "mac": "00:00:00:00:04:04", "ip": "10.0.0.4" },
        "h05": { "mac": "00:00:00:00:05:05", "ip": "10.0.0.5" }
#         "h01": {},
#         "h02": {},
#         "h03": {},
#         "h04": {},
#         "h05": {}
    },
    "links": [
        # Note that multiple links between nodes are unsupported (if declared, single link will be created).
        {
            "node1": "sw01",
            "node2": "sw02"
        },{
            "node1": "sw02",
            "node2": "sw03"
        },{
            "node1": "sw03",
            "node2": "sw04"
        },{
            "node1": "sw04",
            "node2": "sw05"
        },{
            "node1": "sw05",
            "node2": "sw01"
        },{
            "node1": "h01",
            "node2": "sw01"
        },{
            "node1": "h02",
            "node2": "sw02"
        },{
            "node1": "h03",
            "node2": "sw03"
        },{
            "node1": "h04",
            "node2": "sw04"
        },{
            "node1": "h05",
            "node2": "sw05"
        }
    ]
}