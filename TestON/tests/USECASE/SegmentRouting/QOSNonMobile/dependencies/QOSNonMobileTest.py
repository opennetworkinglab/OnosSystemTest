from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
    Testcaselib as run
from tests.USECASE.SegmentRouting.dependencies.trex import Trex
import json


class QOSNonMobileTest:

    def runTest(self, main, test_idx, n_switches):
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

        main.step("Add and verify Slices and Traffic Classes")
        added_slices = True
        new_flows = 0  # one for every new TC in SLICE and 1 for every Flow Classifier
        for slice_name in main.params["SLICING"]["slices"]:
            slice = main.params["SLICING"]["slices"][slice_name]
            if "slice_id" not in slice:
                continue
            slice_id = int(slice["slice_id"])
            onos_rest.addSlice(slice_id=slice_id, debug=True)
            slices_onos = onos_rest.getSlices(debug=True)
            # Verify the slice has been added
            added_slices = added_slices and \
                           {"SliceId": slice_id} in json.loads(slices_onos)

            tcs = []
            for tc in slice.get("traffic_classes", "").split(","):
                onos_rest.addTrafficClassToSlice(slice_id=slice_id,
                                                 traffic_class=tc,
                                                 debug=True)
                tcs.append({"TrafficClass": tc})
                new_flows += 1
            tcs_onos = onos_rest.getTrafficClasses(slice_id=slice_id,
                                                   debug=True)
            # Verify the TC has been added to the slice
            added_slices = added_slices and \
                           sorted(json.loads(tcs_onos)) == sorted(tcs)
        utilities.assert_equal(
            expect=True,
            actual=added_slices,
            onpass="Slices and Traffic Classes installed in slicing service",
            onfail="Error in installing Slices and Traffic Classes in slicing service"
        )

        main.step("Add and verify slicing traffic classifier")
        flows_in_slicing = True
        for slicing_cfg_name in main.params["SLICING"]["traffic_classification"]:
            new_flows += 1
            slicing_config = main.params["SLICING"]["traffic_classification"][
                slicing_cfg_name]

            traffic_selector = self.__cleanupTrafficSelector(slicing_config.get("traffic_selector", []))
            onos_rest.addSlicingClassifierFlow(
                slice_id=int(slicing_config.get("slice_id", "0")),
                traffic_class=slicing_config.get("traffic_class",
                                                 "BEST_EFFORT"),
                traffic_selector=traffic_selector,
                debug=True
            )
            # Verify classifier flows
            onos_flows = json.loads(onos_rest.getSlicingClassifierFlow(
                slice_id=int(slicing_config.get("slice_id", "0")),
                traffic_class=slicing_config.get("traffic_class",
                                                 "BEST_EFFORT"),
                debug=True
            ))
            flows_in_slicing = flows_in_slicing and traffic_selector in onos_flows

        utilities.assert_equal(
            expect=True,
            actual=flows_in_slicing,
            onpass="Traffic Classifier Flows installed in slicing service",
            onfail="Error in installing Classifier Flows in slicing service"
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

        main.step("Remove and verify slicing traffic classifier")
        no_flows_in_slicing = True
        for slicing_cfg_name in main.params["SLICING"]["traffic_classification"]:
            slicing_config = main.params["SLICING"]["traffic_classification"][
                slicing_cfg_name]

            traffic_selector = self.__cleanupTrafficSelector(slicing_config.get("traffic_selector", []))
            onos_rest.removeSlicingClassifierFlow(
                slice_id=int(slicing_config.get("slice_id", "0")),
                traffic_class=slicing_config.get("traffic_class",
                                                 "BEST_EFFORT"),
                traffic_selector=traffic_selector,
                debug=True
            )
            flow = onos_rest.getSlicingClassifierFlow(
                slice_id=int(slicing_config.get("slice_id", "0")),
                traffic_class=slicing_config.get("traffic_class",
                                                 "BEST_EFFORT"),
                debug=True
            )
            no_flows_in_slicing = no_flows_in_slicing and flow == "[]"

        utilities.assert_equal(
            expect=True,
            actual=no_flows_in_slicing,
            onpass="Traffic Classifier Flows removed in slicing service",
            onfail="Error in removing Classifier Flows in slicing service"
        )

        main.step("Remove and verify Slices and Traffic Classes")
        removed_slices = []
        for slice_name in main.params["SLICING"]["slices"]:
            slice = main.params["SLICING"]["slices"][slice_name]
            if "slice_id" not in slice:
                continue
            slice_id = int(slice["slice_id"])
            for tc in slice.get("traffic_classes", "").split(","):
                # BEST_EFFORT must be removed as last, or we can leave it,
                # it will be removed when removing the slice
                if tc != "BEST_EFFORT":
                    onos_rest.removeTrafficClassToSlice(slice_id=slice_id,
                                                        traffic_class=tc,
                                                        debug=True)
            # Do not try to remove the Default Slice!
            if slice_id != 0:
                onos_rest.removeSlice(slice_id=slice_id, debug=True)
                removed_slices.append(slice_id)

        slices_onos = json.loads(onos_rest.getSlices(debug=True))
        utilities.assert_equal(
            expect=True,
            actual=not any([{"SliceId": slice_id} in slices_onos for slice_id in
                            removed_slices]),
            onpass="Slices and Traffic Classes removed from slicing service",
            onfail="Error in removing Slices and Traffic Classes from slicing service"
        )

        run.checkFlows(main, minFlowCount=original_flows_number)

        main.step("Teardown")
        trex.teardown()
        run.saveOnosDiagsIfFailure(main)
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
