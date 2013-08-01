/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

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
public class TestSelectStepTable {
    public Label testStepId;
    public Label testStepName;
    public Label testStepStatus;
    
    public TestSelectStepTable() {
        
    }
    public TestSelectStepTable(Label stepId, Label stepName) {
        
        this.testStepId = stepId;
        this.testStepName = stepName;
        
        
    }
    
  
     public Label getTestStepId() {
        return  testStepId;
    }
    public void setTestStepId(Label newStepId) {
        testStepId = newStepId;
    }
    public Label getTestStepName() {
        return  testStepName;
    }
    public void setTestStepName(Label newStepName) {
        testStepName = newStepName;
   }
      
}
