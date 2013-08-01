/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import javafx.scene.control.CheckBox;
import javafx.scene.control.Label;

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
public class TestCaseSelectionTable {
    
    public CheckBox testCaseIdCheck;
    public Label testCaseId;
    public Label testCaseName;
    public TestCaseSelectionTable() {
        
    }
    public TestCaseSelectionTable(CheckBox idCheck, Label caseId, Label caseName) {
        this.testCaseIdCheck = idCheck;
        this.testCaseId = caseId;
        this.testCaseName = caseName;
    }
    
    public CheckBox getTestCaseCheckBox() {
        return  testCaseIdCheck;
    }
    public void setTestCaseCheckBox(CheckBox newCheck) {
        testCaseIdCheck = newCheck;
    }
     
    public Label getTestCaseId() {
        return  testCaseId;
    }
    public void setTestCaseId(Label newCaseId) {
        testCaseId = newCaseId;
    }
    public Label getTestCaseName() {
        return  testCaseName;
    }
    public void setTestCaseName(Label newCaseName) {
        testCaseName = newCaseName;
    }
}
