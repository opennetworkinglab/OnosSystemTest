from deepinsight.client import DeepInsightClient
from drivers.common.apidriver import API

class DeepInsightApiDriver( API ):
    def __init__( self ):
        self.name = None
        self.serverUrl = None
        self.accessToken = None
        self.refreshToken = None
        self.requestAuthHeader = None
        self.verifySsl = False
        self.client = None
        super( DeepInsightApiDriver, self ).__init__()

    def connect(
        self,
        **connectargs
    ):
        for key in connectargs:
            vars(self)[key] = connectargs[key]
        self.name = self.options["name"]
        self.client = DeepInsightClient(
            server_url = self.options["server_url"],
            username = self.options["username"],
            password = self.options["password"],
            verify_ssl = self.options["verify_ssl"] == "True",
        )
        self.handle = super( DeepInsightApiDriver, self ).connect()
        return self.handle

    def disconnect( self, **connectargs ):
        self.client.logout()

    def getFlows(
        self,
        startTimeMs = None,
        endTimeMs = None,
        maxResults = 100,
        srcIp = None,
        dstIp = None,
        srcPort = None,
        dstPort = None,
        ipProto = None,
    ):
        return self.client.get_flows(
            startTimeMs,
            endTimeMs,
            maxResults,
            srcIp,
            dstIp,
            srcPort,
            dstPort,
            ipProto,
        )

    def getSwitchPacketDrop(
        self,
        switchId,
        egressPort = 0,
        queueId = 0,
        startTime = None,
        endTime = None,
        numBuckets = 100,
    ):
        return self.client.get_switch_packet_drop(
            switchId,
            egressPort,
            queueId,
            startTime,
            endTime,
            numBuckets,
        )

    def getSwitchAnomalies(
        self, switchId, startTime = None, endTime = None
    ):
        return self.client.get_switch_anomalies(
            switchId, startTime, endTime
        )

    def getSwitchLatencies(
        self,
        switchId,
        startTime = None,
        endTime = None,
        granularity = 1000,
    ):
        return self.client.get_switch_latencies(
            switchId,
            startTime,
            endTime,
            granularity,
        )
