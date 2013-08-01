/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;


import java.text.MessageFormat;
import java.util.*;

/**
 *
 * @author Raghav Kashyap (raghavkashyap@paxterrasolutions.com)
	
 *   TestON is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 2 of the License, or
 *   (at your option) any later version.

 *   TestON is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.

 *   You should have received a copy of the GNU General Public License
 *   along with TestON.  If not, see <http://www.gnu.org/licenses/>.

 */
public class TAILocale {
    
    String fileMenu, viewMenu, editMenu, helpMenu, runMenu,OFAHarnessPath,hierarchyTestON;
    String New, newTestScript, newParams, newTopology,newDriver;
    String open, save, saveAs, saveAll, close, closeAll, exit;
    String copy, cut, paste, select, selectAll, pauseTest, resumeTest, stopTest,aboutHelp;
    String driverExplorer, logExplorer, ProjectExplorer;
    String contextNew, contextTest, contextTpl, contextParam, contextOpen, contextCut, contextCopy, contextPaste, contextDelete, contextRefresh;
    String wizTitle, wiz_Previous, wizN_ext, wizCancel, wiz_Finish, wizTestName, wizTestParams, wizEmailId, wizNumberofTestCases, wizEstimatedTime, wizProject, wizParamName, wizTopologyName;
    String wizProjectWizardId, wizTestWizardId, wizTopologyWizardId;
    String topoTitle, topoProperties, topoInterfaces, topoAttribute, topoValue, topoHost, topoUserName, topoPassword, topoTransport;
    String topoSSH, topoTELNET, topoFTP, topoRLOGIN, topoPrompt, topoSave, topoDefault, topoCancel, topoAttribue, topoValues;
    String testSummaryEndTest, testSummaryTestSummary, testSummaryEnterComment, testSummaryConsoleOutput, summary, information;
    String testSummaryViewLog, testSummaryExecutionStatus, testSummaryTestCaseId, testSummaryTestCaseName, testSummaryTestCaseTitle, testSummaryStartTest;
    String testParameterTestDirctory, testParameteremailId, testParameterSelectTestCase, testParameterStartTest, testParameterCancel;
    
    public TAILocale(Locale currentLocale){
        TAIProperties resource = new TAIProperties();
        MessageFormat messageFormat = new MessageFormat("");
        messageFormat.setLocale(currentLocale);
        
        hierarchyTestON = (String) resource.handleObject("hierarchyTestON");
        OFAHarnessPath =  (String) resource.handleObject("OFAHarnessPath");
        fileMenu = (String) resource.handleObject("File");
        viewMenu = (String) resource.handleObject("View");
        editMenu = (String) resource.handleObject("Edit");
        helpMenu= (String) resource.handleObject("Help");
        runMenu = (String) resource.handleObject("Run");
        pauseTest = (String) resource.handleObject("Pause");
        resumeTest = (String) resource.handleObject("Resume");
        stopTest = (String) resource.handleObject("Stop");
        aboutHelp = (String) resource.handleObject("About");
        driverExplorer = (String) resource.handleObject("DriverExplorer");
        logExplorer= (String) resource.handleObject("LogExplorer");
        ProjectExplorer = (String) resource.handleObject("ProjectExplorer");
        copy = (String) resource.handleObject("Copy");
        cut = (String) resource.handleObject("Cut");
        paste = (String) resource.handleObject("Paste");
        select = (String) resource.handleObject("Select");
        selectAll = (String) resource.handleObject("Select All");
        New =  (String) resource.handleObject("New");
        open = (String) resource.handleObject("Open");
        save = (String) resource.handleObject("Save");
        saveAs = (String) resource.handleObject("SaveAs");
        saveAll = (String) resource.handleObject("Save All");
        close = (String) resource.handleObject("Close");
        closeAll = (String) resource.handleObject("CloseAll");
        exit = (String) resource.handleObject("Exit");
        newDriver = (String) resource.handleObject("Driver");
        newTestScript = (String) resource.handleObject("newTestScript");
        newParams = (String) resource.handleObject("Params");
        newTopology = (String) resource.handleObject("Topology");
        
        // project explorer context menu

        contextNew = (String) resource.handleObject("New");
        contextTest = (String) resource.handleObject("Test");

        contextParam = (String) resource.handleObject("Params");
        contextTpl = (String) resource.handleObject("Tpl");

        contextOpen = (String) resource.handleObject("Open");
        contextCut = (String) resource.handleObject("Cut");

        contextCopy = (String) resource.handleObject("Copy");;
        contextPaste = (String) resource.handleObject("Paste");

        contextRefresh = (String) resource.handleObject("Refresh");
        contextDelete = (String) resource.handleObject("Delete");
        
        //OFA Wizards
        wizTitle = (String) resource.handleObject("wizTitle");
        wiz_Previous = (String) resource.handleObject("wiz_Previous");
        wizN_ext = (String) resource.handleObject("wizN_ext");
        wizCancel = (String) resource.handleObject("wizCancel");
        wiz_Finish = (String) resource.handleObject("wiz_Finish");

        wizTestName = (String) resource.handleObject("wizTestName");
        wizTestParams = (String) resource.handleObject("wizTestParams");
        wizEmailId = (String) resource.handleObject("wizEmailId");
        wizNumberofTestCases = (String) resource.handleObject("wizNumberofTestCases");
        wizEstimatedTime = (String) resource.handleObject("wizEstimatedTime");
        wizProject = (String) resource.handleObject("wizProject");
        wizParamName = (String) resource.handleObject("wizParamName");
        wizTopologyName = (String) resource.handleObject("wizTopologyName");


        wizProjectWizardId = (String) resource.handleObject("wizProjectWizardId");
        wizTestWizardId = (String) resource.handleObject("wizTestWizardId");
        wizTopologyWizardId = (String) resource.handleObject("wizTopologyWizardId");

        // OFA Topology 

        topoTitle = (String) resource.handleObject("topoTitle");
        topoProperties = (String) resource.handleObject("topoProperties");
        topoInterfaces = (String) resource.handleObject("topoInterfaces");
        topoAttribute = (String) resource.handleObject("topoAttribute");
        topoValue = (String) resource.handleObject("topoValue");
        topoHost = (String) resource.handleObject("topoHost");
        topoUserName = (String) resource.handleObject("topoUserName");
        topoPassword = (String) resource.handleObject("topoPassword");
        topoTransport = (String) resource.handleObject("topoTransport");
        topoSSH = (String) resource.handleObject("topoSSH");
        topoTELNET = (String) resource.handleObject("topoTELNET");
        topoFTP = (String) resource.handleObject("topoFTP");
        topoRLOGIN = (String) resource.handleObject("topoRLOGIN");
        topoPrompt = (String) resource.handleObject("topoPrompt");
        topoSave = (String) resource.handleObject("topoSave");
        topoDefault = (String) resource.handleObject("topoDefault");
        topoCancel = (String) resource.handleObject("topoCancel");
        topoValues = (String) resource.handleObject("topoValues");
        
        // OFA Test Summary

        testSummaryViewLog = (String) resource.handleObject("testSummaryViewLog");
        testSummaryTestCaseTitle = (String) resource.handleObject("testSummaryExecutionStatus");
        testSummaryTestCaseId = (String) resource.handleObject("testSummaryTestCaseId");
        testSummaryTestCaseName = (String) resource.handleObject("testSummaryTestCaseName");
        testSummaryExecutionStatus = (String) resource.handleObject("testSummaryTestCaseStatus");
        testSummaryStartTest = (String) resource.handleObject("testSummaryStartTest");
        testSummaryEndTest = (String) resource.handleObject("testSummaryEndTest");
        testSummaryTestSummary = (String) resource.handleObject("testSummaryTestSummary");
        summary = (String) resource.handleObject("summary");
        information = (String) resource.handleObject("information");
        testSummaryEnterComment = (String) resource.handleObject("testSummaryEnterComment");
        testSummaryConsoleOutput = (String) resource.handleObject("testSummaryConsoleOutput");
        testParameterCancel = (String) resource.handleObject("testParameterCancel");

        
        
    }
}
