
class SpirentTest :

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :

        main.case("Basic Spirent test")
        main.step("Check if handle is created")
        main.log.info("Handle created successfully")
    
        mintraffic = '400000'
        minbitpercent = '9.00000000'
        chassisAddress = '10.254.1.102'
        slot = '1'
        p1 = '1'
        p2 = '2'
    
        main.case("Creating a Project")
        main.step("Checking the creation of project")
        project = main.Stc1.create('project', name='project1')
    
        main.step("Get Project attributes")
        projectAtt = main.Stc1.get(project ,'name')
    
    
    
        main.step("Creating ports under the Project")
        port1 = main.Stc1.create('port',under=project)
        port2 = main.Stc1.create('port',under=project)
    
        main.step("configuring the port locations")
        main.Stc1.config(port1, location="//%s/%s/%s" % (chassisAddress, slot,p1))
        main.Stc1.config(port2, location="//%s/%s/%s" % (chassisAddress, slot,p2))
    
        main.step("Creating streamBlock on port1")
        streamBlock = main.Stc1.create('streamBlock',under=port1)
        generator = main.Stc1.get(port1,'children-generator')
        analyzer = main.Stc1.get(port2,'children-Analyzer')
    
    
        main.step("Attaching Ports...")
        main.Stc1.perform('AttachPorts', portList = [port1 , port2], autoConnect='TRUE')
        main.Stc1.apply ()
    
        main.case("Subscribe the ports ports from Project")
        main.step("Call Subscribe...")
        port1GeneratorResult    = main.Stc1.subscribe(Parent=project, ResultParent=port1, ConfigType='Generator', resulttype='GeneratorPortResults', filenameprefix="Generator_port1_counter%s"% port1 ,Interval='2')
        port2AnalyzerResult = main.Stc1.subscribe(Parent=project, ResultParent=port2, ConfigType='Analyzer', resulttype='AnalyzerPortResults',filenameprefix="Analyzer_port2_counter%s"% port2)
    
        main.step("Starting traffic")
        main.Stc1.perform('AnalyzerStart', analyzerList=analyzer)
    
        main.step("Start Analyzer")
        main.log.info("# wait for analyzer to start"    )
        main.Stc1.sleep(1)
        main.Stc1.perform('GeneratorStart', generatorList=generator)
    
        main.step("Sleep 5 seconds...")
        main.log.info("# generate traffic for 5 seconds"    )
        main.Stc1.sleep(5)
    
        main.step("Stopping Traffic...")
        main.log.info("stop generator")
        main.Stc1.perform('GeneratorStop', generatorList=generator)
        main.log.info("Stop analyzer")
        main.Stc1.perform('AnalyzerStop', analyzerList=analyzer)
    
        main.step("Call Unsubscribe...")
        main.Stc1.unsubscribe(port2AnalyzerResult)
        main.Stc1.unsubscribe(port1GeneratorResult)
    
        main.step("Call Disconnect...")
        main.Stc1.disconnect(chassisAddress)
        main.Stc1.delete(project)
    
        main.log.info("##############################Checking Analyzer port results###################################")
        main.step("Checking the result of ResultObject")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="ResultObject")
        utilities.assert_equals(expect=str(result),actual=result,onpass="Resultobject passed",onfail="resultobject not getting")
    
        main.step("Checking the result for TotalFrameCount")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="ResultObjectName")
        utilities.assert_equals(expect=str(result),actual=result,onpass="ResultObjectName is getting",onfail="ResultObjectName not getting")
    
        main.step("Checking for ResultParent value")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="ResultParent")
        utilities.assert_equals(expect=str(result),actual=result,onpass="ResultParent is getting",onfail="ResultParent not getting")
    
        main.step("Checking ResultParentName in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="ResultParentName")
        utilities.assert_matches(expect=str(result),actual=result,onpass="ResultParentName is getting",onfail="ResultParentName not getting")
    
        main.step("Checking TotalFrameCount in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="TotalFrameCount")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="TotalFrameCount is getting",onfail="TotalFrameCount not getting")
    
        main.step("Checking TotalOctetCount in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="TotalOctetCount")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="TotalOctetCount is getting",onfail="TotalOctetCount not getting")
    
        main.step("Checking SigFrameCount in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="SigFrameCount")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="SigFrameCount is getting",onfail="SigFrameCount not getting")
    
        main.step("Checking TotalFrameRate in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="TotalFrameRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="TotalFrameRate is getting",onfail="TotalFrameRate not getting")
    
        main.step("Checking TotalOctetRate in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="TotalOctetRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="TotalOctetRate is getting",onfail="TotalOctetRate not getting")
    
        main.step("Checking TotalBitRate in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="TotalBitRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="TotalBitRate is getting",onfail="TotalBitRate not getting")
    
        main.step("Checking TotalBitCount in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="TotalBitCount")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="TotalBitCount is getting",onfail="TotalBitCount not getting")
    
        main.step("Checking L1BitCount in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="L1BitCount")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="L1BitCount is getting",onfail="L1BitCount not getting")
    
        main.step("Checking L1BitRate in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="L1BitRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="L1BitRate is getting",onfail="L1BitRate not getting")
    
        main.step("Checking L1BitRatePercent in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="L1BitRatePercent")
        utilities.assert_greater(expect=result,actual=minbitpercent,onpass="L1BitRatePercent is getting",onfail="L1BitRatePercent not getting")
    
        main.step("Checking SigFrameRate in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="SigFrameRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="SigFrameRate is getting",onfail="SigFrameRate not getting")
    
        main.step("Checking PrbsFillOctetRate in results")
        result = main.Stc1.parseresults(CsvFile='Analyzer_port2_counterport2.csv',Attribute="PrbsFillOctetRate")
        utilities.assert_equals(expect=result,actual=main.FALSE,onpass="PrbsFillOctetRate is not getting",onfail="PrbsFillOctetRate is getting")
    
        main.log.info("##############################Checking Generator port results################################" )
        main.step("Checking ResultObject in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="ResultObject")
        utilities.assert_equals(expect=result,actual=str(result),onpass="Resultobject passed",onfail="resultobject not getting")
    
        main.step("Checking ResultObjectName in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="ResultObjectName")
        utilities.assert_equals(expect=result,actual=str(result),onpass="ResultObjectName is getting",onfail="ResultObjectName not getting")
    
        main.step("Checking ResultParent in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="ResultParent")
        utilities.assert_equals(expect=result,actual=str(result),onpass="ResultParent is getting",onfail="ResultParent not getting")
    
        main.step("Checking ResultParentName in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="ResultParentName")
        utilities.assert_equals(expect=result,actual=str(result),onpass="ResultParentName is getting",onfail="ResultParentName not getting")
    
        main.step("Checking TotalFrameCount in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="TotalFrameCount")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="TotalFrameCount is getting",onfail="TotalFrameCount not getting")
    
        main.step("Checking TotalOctetCount in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="TotalOctetCount")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="TotalOctetCount is getting",onfail="TotalOctetCount not getting")
    
        main.step("Checking GeneratorFrameCount in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="GeneratorFrameCount")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="GeneratorFrameCount is getting",onfail="GeneratorFrameCount not getting")
    
        main.step("Checking GeneratorSigFrameCount in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="GeneratorSigFrameCount")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="GeneratorSigFrameCount is getting",onfail="GeneratorSigFrameCount not getting")
    
        main.step("Checking for GeneratorOctetCount value")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="GeneratorOctetCount")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="GeneratorOctetCount is getting",onfail="GeneratorOctetCount not getting")
    
        main.step("Checking TotalFrameRate in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="TotalFrameRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="TotalFrameRate is getting",onfail="TotalFrameRate not getting")
    
        main.step("Checking TotalOctetRate in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="TotalOctetRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="TotalOctetRate is getting",onfail="TotalOctetRate not getting")
    
        main.step("Checking TotalBitRate in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="TotalBitRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="TotalBitRate is getting",onfail="TotalBitRate not getting")
    
        main.step("Checking TotalBitCount in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="TotalBitCount")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="TotalBitCount is getting",onfail="TotalBitCount not getting")
    
        main.step("Checking L1BitCount in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="L1BitCount")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="L1BitCount is getting",onfail="L1BitCount not getting")
    
        main.step("Checking L1BitRate in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="L1BitRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="L1BitRate is getting",onfail="L1BitRate not getting")
    
        main.step("Checking L1BitRatePercent in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="L1BitRatePercent")
        utilities.assert_greater(expect=result,actual=minbitpercent,onpass="L1BitRatePercent is getting",onfail="L1BitRatePercent not getting")
    
        main.step("Checking GeneratorFrameRate in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="GeneratorFrameRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="GeneratorFrameRate is getting",onfail="GeneratorFrameRate not getting")
    
        main.step("Checking GeneratorSigFrameRate in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="GeneratorSigFrameRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="GeneratorSigFrameRate is getting",onfail="GeneratorSigFrameRate not getting")
    
        main.step("Checking GeneratorOctetRate in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="GeneratorOctetRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="GeneratorOctetRate is getting",onfail="GeneratorOctetRate not getting")
    
        main.step("Checking GeneratorBitRate in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="GeneratorBitRate")
        utilities.assert_greater(expect=result,actual=mintraffic,onpass="GeneratorBitRate is getting",onfail="GeneratorBitRate not getting")
    
        main.step("Checking TotalIpv4FrameRate in results")
        result = main.Stc1.parseresults(CsvFile='Generator_port1_counterport1.csv',Attribute="TotalIpv4FrameRate")
        utilities.assert_equals(expect=result,actual=main.FALSE,onpass="TotalIpv4FrameRate is not getting",onfail="TotalIpv4FrameRate is getting")
    
    
    