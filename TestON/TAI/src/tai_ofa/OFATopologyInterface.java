/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import javafx.scene.control.Label;
import javafx.scene.control.TextField;

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
public class OFATopologyInterface {
    public Label interFaceNumber; 
    private TextField deviceName;
    private  TextField deviceType;
     

    
    public OFATopologyInterface(Label emailtext,TextField deviceNameText,TextField deviceTypeText){
            this.deviceName = deviceNameText;
            this.deviceType = deviceTypeText;
            this.interFaceNumber = emailtext;
    }
     
        public TextField getDeviceName() {
            return deviceName;
        }
        public void setDeviceName(TextField fName) {
            deviceName = fName;
        }
        
        public TextField getDeviceType() {
            return deviceType;
        }
        public void setDeviceType(TextField fName) {
            deviceType = fName;
        }
        
        public Label getInterFaceNumber() {
            return interFaceNumber;
        }
        public void setInterFaceNumber(Label fName) {
            interFaceNumber = fName;
        }
}

    

