/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;
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
public class TAIProperties extends ResourceBundle {
    
    public Object handleObject(String key){
      //Set TestON Hierarchy path here
        if (key.equals("hierarchyTestON")){
            return "/home/paxterra/Desktop/TestON/";
        }
        
        
       if (key.equals("OFAHarnessPath")){
            return "/home/paxterra/Music/TAI_OFA/src/";
        }    
                
        if (key.equals("File")){
            return "File";
        }
        
        if (key.equals("View")) {
            return "View";
        }
        
        if (key.equals("Run")){
            return "Run";
        }
        
        if (key.equals("Edit")){
            return "Edit";
        }
        
        if (key.equals("Help")){
            return "Help";
        }
        
        if (key.equals("New")){
            return "New";
        }
        
        if (key.equals("Open")){
            return "Open";
        }
        
        if(key.equals("Pause")) {
            return "Pause";
        }
        if(key.equals("Resume")) {
            return "Resume";
        }
        if(key.equals("Stop")) {
            return "Stop";
        }
        if(key.equals("About")) {
            return "About";
        }
        
        if(key.equals("DriverExplorer")) {
            return "Driver Explorer";
        }
        
        if(key.equals("ProjectExplorer")) {
            return "Project Explorer";
        }
        
        if(key.equals("LogExplorer")) {
            return "Log Explorer";
        }
        
        if(key.equals("Cut")) {
            return "Cut";
        }
        if(key.equals("Copy")) {
            return "Copy";
        }
        
        if(key.equals("Paste")) {
            return "Paste";
        }
        
        if(key.equals("Select")) {
            return "Select";
        }
        if(key.equals("Select All")) {
            return "Select All";
        }
        if(key.equals("Save")) {
            return "Save";
        }
        if(key.equals("SaveAs")) {
            return "Save As";
        }
        
        if(key.equals("Save All")) {
            return "SaveAll";
        }
        
        if(key.equals("Close")) {
            return "Close";
        }
        if(key.equals("CloseAll")) {
            return "CloseAll";
        }
        if(key.equals("Exit")) {
            return "Exit";
        }
        
        if(key.equals("Exit")) {
            return "Exit";
        }
        
        if(key.equals("Driver")) {
            return "Component Driver";
        }
        if(key.equals("Params")) {
            return "Params";
        }
        if(key.equals("Topology")) {
            return "Topology";
        }
        if(key.equals("newTestScript")) {
            return "Test Script";
        }
        
        //Context Menu
         if (key.equals("New")) {
            return "New";
        }

        if (key.equals("Test")) {
            return "Test";
        }
        if (key.equals("Param")) {
            return "Params";
        }
        if (key.equals("Tpl")) {
            return "TPL";
        }

        if (key.equals("Open")) {
            return "Open";
        }

        if (key.equals("Cut")) {
            return "Cut";
        }

        if (key.equals("Copy")) {
            return "Copy";
        }

        if (key.equals("Paste")) {
            return "Paste";
        }
        if (key.equals("Refresh")) {
            return "Refresh";
        }

        if (key.equals("Delete")) {
            return "Delete";
        }
        
        //OFA WIZARDS
        if (key.equals("wizTitle")) {
            return "AutoMate";
        }
        if (key.equals("wiz_Previous")) {
            return "_Previous";
        }

        if (key.equals("wizN_ext")) {
            return "N_ext";
        }
        if (key.equals("wizCancel")) {
            return "Cancel";
        }

        if (key.equals("wiz_Finish")) {
            return "_Finish";
        }
        if (key.equals("wizTestName")) {
            return "Test Name";
        }

        if (key.equals("wizTestParams")) {
            return "TEST PARAMS:";
        }
        if (key.equals("wizEmailId")) {
            return "Email Id";
        }

        if (key.equals("wizNumberofTestCases")) {
            return "Number of TestCases";
        }
        if (key.equals("wizEstimatedTime")) {
            return "Estimated Time";
        }

        if (key.equals("wizProject")) {
            return "Project";
        }
        if (key.equals("wizParamName")) {
            return "Param Name";
        }

        if (key.equals("wizTopologyName")) {
            return "Topology Name";
        }
        if (key.equals("wizProjectWizardId")) {
            return "projectWizard";
        }

        if (key.equals("wizTestWizardId")) {
            return "testWizard";
        }
        if (key.equals("wizTopologyWizardId")) {
            return "topologyWizard";
        }

        if (key.equals("wiz")) {
            return "Attribue";
        }
        if (key.equals("wiz")) {
            return "Values";
        }
            
        // OFA Topology

        if (key.equals("topoTitle")) {
            return "Topology";
        }
        if (key.equals("topoProperties")) {
            return "Properties";
        }

        if (key.equals("topoInterfaces")) {
            return "Interfaces";
        }
        if (key.equals("topoAttribute")) {
            return "Attribute";
        }

        if (key.equals("topoValue")) {
            return "Value";
        }

        if (key.equals("topoHost")) {
            return "Host";
        }
        if (key.equals("topoUserName")) {
            return "User Name";
        }
        if (key.equals("topoPassword")) {
            return "Password";
        }
        if (key.equals("topoTransport")) {
            return "Transport";
        }

        if (key.equals("topoSSH")) {
            return "SSH";
        }

        if (key.equals("topoTELNET")) {
            return "TELNET";
        }
        if (key.equals("topoFTP")) {
            return "FTP";
        }
        if (key.equals("topoRLOGIN")) {
            return "RLOGIN";
        }



        if (key.equals("topoPrompt")) {
            return "Prompt";
        }

        if (key.equals("topoSave")) {
            return "Save";
        }
        if (key.equals("topoDefault")) {
            return "Default";
        }
        if (key.equals("topoCancel")) {
            return "Cancel";
        }


        if (key.equals("topoInterfaces")) {
            return "Interfaces";
        }
        if (key.equals("topoAttribue")) {
            return "Attribue";
        }
        if (key.equals("topoValues")) {
            return "Values";
        }




             
        // OFA TestSummary


        if (key.equals("testSummaryViewLog")) {
            return "View Logs";
        }
        if (key.equals("testSummaryExecutionStatus")) {
            return "Execution Status";
        }

        if (key.equals("testSummaryTestCaseId")) {
            return "ID";
        }
        if (key.equals("testSummaryTestCaseName")) {
            return "Name";
        }

        if (key.equals("testSummaryTestCaseStatus")) {
            return "Status";
        }

        if (key.equals("testSummaryStartTest")) {
            return "Start Test";
        }
        if (key.equals("testSummaryEndTest")) {
            return "End Test";
        }
        if (key.equals("summary")) {
            return "Summary";
        }
        if (key.equals("information")) {
            return "Information";
        }

        if (key.equals("testSummaryTestSummary")) {
            return "Test Summary";
        }

        if (key.equals("testSummaryEnterComment")) {
            return "Test Summary Console";
        }
        if (key.equals("testSummaryConsoleOutput")) {
            return "Console output";
        }
        
     return null;     
    }

    @Override
    protected Set<String> handleGetObject(String key) {
        
        return new HashSet<String>(Arrays.asList("okKey", "cancelKey"));
    }

    @Override
    public Enumeration<String> getKeys() {
        return Collections.enumeration(keySet());
    }
    
}
