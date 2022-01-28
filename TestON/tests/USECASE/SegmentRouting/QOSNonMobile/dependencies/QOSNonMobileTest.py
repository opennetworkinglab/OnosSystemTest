from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
    Testcaselib as run
from tests.USECASE.SegmentRouting.dependencies.trex import Trex
import json


class QOSNonMobileTest:

    def runTest(self, main, test_idx, n_switches):
        try:
            run.initTest(main)
            main.log.info(main.Cluster.numCtrls)
            main.Cluster.setRunningNode(3)
            run.installOnos(main, skipPackage=True, cliSleep=5)

            # Use the first available ONOS instance CLI
            onos_rest = main.Cluster.active(0).REST
            onos_cli = main.Cluster.active(0).CLI

            # Load traffic config for the current test case
            cfgFile = "%s/tests/CASE_%d.json" % (main.configPath, test_idx)
            with open(cfgFile) as cfg:
                testCfg = json.load(cfg)

            trex = Trex()
            trex.setup(main.TRexClient)

            original_flows_number = onos_cli.checkFlowCount()

            main.step("Verify slices and traffic Classes")

            slices_onos = onos_rest.getSlices(debug=True)

            # Sanity check for the API, at least the default slice should be there.
            utilities.assert_equal(
                expect=True,
                actual={"SliceId": 0} in json.loads(slices_onos),
                onpass="Default slice verified in slicing service",
                onfail="Error in verifying default slice in slicing service"
            )

            for slice_name in main.params["SLICING"]["slices"]:
                slice = main.params["SLICING"]["slices"][slice_name]
                if "slice_id" not in slice:
                    continue
                slice_id = int(slice["slice_id"])
                utilities.assert_equal(
                    expect=True,
                    actual={"SliceId": slice_id} in json.loads(slices_onos),
                    onpass="Verified presence of slice %s in slicing service" % slice_id,
                    onfail="Slice %s not found in slicing service" % slice_id
                )

                tcs = slice.get("traffic_classes", "").split(",")

                tcs_onos = onos_rest.getTrafficClasses(slice_id=slice_id,
                                                       debug=True)
                for tc in tcs:
                    utilities.assert_equal(
                        expect=True,
                        actual={"TrafficClass": tc} in json.loads(tcs_onos),
                        onpass="Verified presence of TC %s for slice %s in slicing service" % (tc, slice_id),
                        onfail="TC %s not found for slice %s in slicing service" % (tc, slice_id)
                    )

            main.step("Add and verify traffic classifier flows")
            new_flows = 0
            for flow_name in main.params["SLICING"]["traffic_classification"]:
                new_flows += 1
                flow_config = main.params["SLICING"]["traffic_classification"][
                    flow_name]

                traffic_selector = self.__cleanupTrafficSelector(flow_config.get("traffic_selector", []))
                onos_rest.addSlicingClassifierFlow(
                    slice_id=int(flow_config.get("slice_id")),
                    traffic_class=flow_config.get("traffic_class"),
                    traffic_selector=traffic_selector,
                    debug=True
                )

                onos_flows = json.loads(onos_rest.getSlicingClassifierFlow(
                    slice_id=int(flow_config.get("slice_id")),
                    traffic_class=flow_config.get("traffic_class"),
                    debug=True
                ))
                utilities.assert_equal(
                    expect=True,
                    actual=traffic_selector in onos_flows,
                    onpass="Classifier flow %s installed" % flow_name,
                    onfail="Classifier flow %s not found after insert" % flow_name
                )

            run.checkFlows(
                main,
                minFlowCount=original_flows_number + (new_flows * n_switches)
            )

            main.step("Send traffic with TRex")
            for flow in testCfg["flows"]:
                trex.createFlow(flow)
            results = trex.sendAndReceiveTraffic(testCfg["duration"])
            trex.verifyCongestion(results)

            trex.logPortStats()
            for flow in testCfg["flows"]:
                trex.logFlowStats(flow)

            # Assert Flow Stats
            for flow in testCfg["flows"]:
                if trex.isFlowStats(flow):
                    main.step("{}: Assert RX Packets".format(flow))
                    trex.assertRxPackets(flow)
                    main.step("{}: Assert Dropped Packets".format(flow))
                    trex.assertDroppedPacket(flow)
                    main.step("{}: Assert 99.9 Percentile Latency".format(flow))
                    trex.assert99_9PercentileLatency(flow)

            main.step("Remove and verify traffic classifier flows")
            for flow_name in main.params["SLICING"]["traffic_classification"]:
                flow_config = main.params["SLICING"]["traffic_classification"][
                    flow_name]

                traffic_selector = self.__cleanupTrafficSelector(flow_config.get("traffic_selector", []))
                onos_rest.removeSlicingClassifierFlow(
                    slice_id=int(flow_config.get("slice_id")),
                    traffic_class=flow_config.get("traffic_class"),
                    traffic_selector=traffic_selector,
                    debug=True
                )
                onos_flow = onos_rest.getSlicingClassifierFlow(
                    slice_id=int(flow_config.get("slice_id")),
                    traffic_class=flow_config.get("traffic_class"),
                    debug=True
                )
                utilities.assert_equal(
                    expect="[]",
                    actual=onos_flow,
                    onpass="Classifier flow %s removed from slicing service" % flow_name,
                    onfail="Unable to remove classifier flow %s from slicing service" % flow_name
                )

            run.checkFlows(main, minFlowCount=original_flows_number)
        finally:
            main.step("Teardown")
            trex.teardown()
            run.cleanup(main)

    def __cleanupTrafficSelector(self, traffic_selector):
        ts = {
            "criteria": [traffic_selector[criteria] for criteria in
                         traffic_selector]}
        # Cleanup the traffic selector, by converting into integer the
        # required fields, conversion is required for checking the result
        # from ONOS
        for criteria in ts["criteria"]:
            if "udpPort" in criteria:
                criteria["udpPort"] = int(criteria["udpPort"])
        return ts
