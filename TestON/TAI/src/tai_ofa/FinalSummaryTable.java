/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import javafx.scene.control.Label;

/**
 *
 * @author Raghav Kashyap raghavkashyap@paxterrasolutions.com
	
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

public class FinalSummaryTable {
    public Label summaryItem;
    public Label information;
    
    public FinalSummaryTable() {
        
    }
    public FinalSummaryTable(Label summaryItem, Label information) {
        
        this.summaryItem = summaryItem;
        this.information = information;
        
    }
    
  
     public Label getSummaryItem() {
        return  summaryItem;
    }
    public void setSummaryItem(Label newSummaryItem) {
        summaryItem = newSummaryItem;
    }
    public Label getInformation() {
        return  information;
    }
    public void setInformation(Label newInformation) {
        information = newInformation;
    }
    
}

