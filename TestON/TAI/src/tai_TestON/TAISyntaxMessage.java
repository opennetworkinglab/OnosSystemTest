/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_TestON;

/**
*
* @author Raghavkashyap (raghavkashyap@paxterra.com)

* TestON is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 2 of the License, or
* (at your option) any later version.

* TestON is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.

* You should have received a copy of the GNU General Public License
* along with TestON. If not, see <http://www.gnu.org/licenses/>.

*/

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

/**
 *
 * @author paxterra
 */
class TAISyntaxMessage {
    ArrayList<String> syntaxError;
    HashMap paramErrorCode;
    HashMap messageAndFixHash = new HashMap();
    HashMap<String, HashMap<String, String>> validationMessage = new HashMap<String, HashMap<String, String>>();
    String errorMessage;
    String errorFixMethod;

    public TAISyntaxMessage() {
    }

    public TAISyntaxMessage(ArrayList errorCode) {
        this.syntaxError = errorCode;

    }

    public HashMap validationMessages() {

        // Param File Error

        messageAndFixHash.put("param100", "closing tag is missing");
        messageAndFixHash.put("fixparam100", "fix_param100()");
        validationMessage.put("param100", messageAndFixHash);


        messageAndFixHash.put("param101", "Please specify number of test case");
        messageAndFixHash.put("fixparam101", "fix_param101()");
        validationMessage.put("param101", messageAndFixHash);


        messageAndFixHash.put("param102", "please specify number of testcase in correct format");
        messageAndFixHash.put("fixparam102", "fix_param102()");
        validationMessage.put("param102", messageAndFixHash);

        messageAndFixHash.put("param103", "Please add testCaseIds");
        messageAndFixHash.put("fixparam103", "fix_param103()");
        validationMessage.put("param103", messageAndFixHash);

        messageAndFixHash.put("param104", "TestCaseId is not in correct format");
        messageAndFixHash.put("fixparam104", "fix_param104()");
        validationMessage.put("param104", messageAndFixHash);

        messageAndFixHash.put("param105", "plese specify estimated time");
        messageAndFixHash.put("fixparam105", "fix_param105()");
        validationMessage.put("param105", messageAndFixHash);

        messageAndFixHash.put("message", "estimated time is not in correct format");
        messageAndFixHash.put("fixparam106", "fix_param106()");
        validationMessage.put("param106", messageAndFixHash);

        messageAndFixHash.put("param107", "plese enter email id");
        messageAndFixHash.put("fixparam107", "fix_param107()");
        validationMessage.put("param107", messageAndFixHash);

        messageAndFixHash.put("param108", "email id  should be a@b.com  form");
        messageAndFixHash.put("fixparam108", "fix_param108()");
        validationMessage.put("param108", messageAndFixHash);

        messageAndFixHash.put("param109", "starting (<) tag is missing");
        messageAndFixHash.put("fixparam109", "fix_param109()");
        validationMessage.put("param109", messageAndFixHash);

        messageAndFixHash.put("param110", "ending (>) tag is missing");
        messageAndFixHash.put("fixparam110", "fix_param110()");
        validationMessage.put("param110", messageAndFixHash);

        messageAndFixHash.put("param111", "please specify log directory");
        messageAndFixHash.put("fixparam111", "fix_param111()");
        validationMessage.put("param111", messageAndFixHash);

        messageAndFixHash.put("param112", "log dir should be /~log/ form ");
        messageAndFixHash.put("fixparam112", "fix_param112()");
        validationMessage.put("param112", messageAndFixHash);

        messageAndFixHash.put("param113", "case parameter is not in correct format");
        messageAndFixHash.put("fixparam113", "fix_param113()");
        validationMessage.put("param113", messageAndFixHash);

        messageAndFixHash.put("param114", "case parameter is not in correct format");
        messageAndFixHash.put("fixparam114", "fix_param114()");
        validationMessage.put("param114", messageAndFixHash);


        //param file warnings

        messageAndFixHash.put("param151", "uninitialized number of testCases");
        messageAndFixHash.put("fixparam151", "fix_param151()");
        validationMessage.put("param151", messageAndFixHash);

        messageAndFixHash.put("param152", "uninitialized number of testCases");
        messageAndFixHash.put("fixparam152", "fix_param152()");
        validationMessage.put("param152", messageAndFixHash);

        messageAndFixHash.put("param153", "uninitialized number of testCases");
        messageAndFixHash.put("fixparam153", "fix_param153()");
        validationMessage.put("param153", messageAndFixHash);

        messageAndFixHash.put("param154", "uninitialized number of testCases");
        messageAndFixHash.put("fixparam154", "fix_param154()");
        validationMessage.put("param151", messageAndFixHash);

        messageAndFixHash.put("param155", "uninitialized number of testCases");
        messageAndFixHash.put("fixparam155", "fix_param155()");
        validationMessage.put("param151", messageAndFixHash);

        messageAndFixHash.put("param156", "uninitialized number of testCases");
        messageAndFixHash.put("fixparam156", "fix_param156()");
        validationMessage.put("param156", messageAndFixHash);

        // param file info 
        messageAndFixHash.put("param201", "please specifty case parameter");
        messageAndFixHash.put("fixparam201", "fix_param201()");
        validationMessage.put("param201", messageAndFixHash);



        // ospk file error
        messageAndFixHash.put("ospk501", "Test Name should be in inverted commas");
        messageAndFixHash.put("fixospk501", "fix_ospk501()");
        validationMessage.put("ospk501", messageAndFixHash);

        messageAndFixHash.put("ospk502", "please add Case number");
        messageAndFixHash.put("fixospk502", "fix_ospk502()");
        validationMessage.put("ospk502", messageAndFixHash);

        messageAndFixHash.put("ospk503", "CASE number is already existing");
        messageAndFixHash.put("fixospk503", "fix_ospk503()");
        validationMessage.put("ospk503", messageAndFixHash);

        messageAndFixHash.put("ospk504", "please add NAME inside inverted commas");
        messageAndFixHash.put("fixospk504", "fix_ospk504()");
        validationMessage.put("ospk504", messageAndFixHash);

        messageAndFixHash.put("ospk505", "please add description inside inverted commas");
        messageAndFixHash.put("fixospk505", "fix_ospk505()");
        validationMessage.put("ospk505", messageAndFixHash);

        messageAndFixHash.put("ospk506", "please add step inside inverted commas");
        messageAndFixHash.put("fixospk506", "fix_ospk506()");
        validationMessage.put("ospk506", messageAndFixHash);

        messageAndFixHash.put("ospk507", "END CASE is not present for this case");
        messageAndFixHash.put("fixospk507", "fix_ospk507()");
        validationMessage.put("ospk507", messageAndFixHash);

        messageAndFixHash.put("ospk508", "please add case number in digits");
        messageAndFixHash.put("fixospk508", "fix_ospk508()");
        validationMessage.put("ospk508", messageAndFixHash);

        messageAndFixHash.put("ospk509", "please add deviceName between ON and RUN");
        messageAndFixHash.put("fixospk509", "fix_ospk509()");
        validationMessage.put("ospk509", messageAndFixHash);

        messageAndFixHash.put("ospk510", "please add function name after RUN");
        messageAndFixHash.put("fixospk510", "fix_ospk510()");
        validationMessage.put("ospk510", messageAndFixHash);

        messageAndFixHash.put("ospk511", "add device name between ON and RUN");
        messageAndFixHash.put("fixospk511", "fix_ospk511()");
        validationMessage.put("ospk511", messageAndFixHash);

        messageAndFixHash.put("ospk512", "add function Name between RUN and WITH");
        messageAndFixHash.put("fixospk512", "fix_ospk512()");
        validationMessage.put("ospk512", messageAndFixHash);

        messageAndFixHash.put("ospk513", "add function Parameter in parameter(user=>CASE{USER})");
        messageAndFixHash.put("fixospk513", "fix_ospk513()");
        validationMessage.put("ospk513", messageAndFixHash);

        messageAndFixHash.put("ospk514", "case parameter is not in correct format");
        messageAndFixHash.put("fixospk514", "fix_ospk514()");
        validationMessage.put("ospk514", messageAndFixHash);

        messageAndFixHash.put("ospk515", "please add varible name to store the result");
        messageAndFixHash.put("fixospk515", "fix_ospk515()");
        validationMessage.put("ospk515", messageAndFixHash);

        messageAndFixHash.put("ospk516", "Assert is not in correct format");
        messageAndFixHash.put("fixospk516", "fix_ospk516()");
        validationMessage.put("ospk516", messageAndFixHash);

        messageAndFixHash.put("ospk517", "variable is not in correct format");
        messageAndFixHash.put("fixospk517", "fix_ospk517()");
        validationMessage.put("ospk517", messageAndFixHash);

        messageAndFixHash.put("ospk518", "ON PASS message should be in inverted commas");
        messageAndFixHash.put("fixospk518", "fix_ospk518()");
        validationMessage.put("ospk518", messageAndFixHash);

        messageAndFixHash.put("ospk519", "ON Fail message should be in inverted commas");
        messageAndFixHash.put("fixospk519", "fix_ospk519()");
        validationMessage.put("ospk519", messageAndFixHash);

        messageAndFixHash.put("ospk520", "ASSERT statement is not in correct format");
        messageAndFixHash.put("fixospk520", "fix_ospk520()");
        validationMessage.put("ospk520", messageAndFixHash);



        // ospk file info

        messageAndFixHash.put("ospk601", "please add TEST NAME");
        messageAndFixHash.put("fixospk601", "fix_ospk601()");
        validationMessage.put("ospk601", messageAndFixHash);
        
        messageAndFixHash.put("ospk602", "please specify NAME");
        messageAndFixHash.put("fixospk602", "fix_ospk602()");
        validationMessage.put("ospk602", messageAndFixHash);
        
        messageAndFixHash.put("ospk603", "please add description");
        messageAndFixHash.put("fixospk603", "fix_ospk603()");
        validationMessage.put("ospk603", messageAndFixHash);
        
        messageAndFixHash.put("ospk604", "please add step");
        messageAndFixHash.put("fixospk604", "fix_ospk604()");
        validationMessage.put("ospk604", messageAndFixHash);
        
        

        return validationMessage;
    }

    public String getMessage(String code) {

        Set validationMessageSet = validationMessages().entrySet();
        Iterator validationMessageSetIterator = validationMessageSet.iterator();
        while (validationMessageSetIterator.hasNext()) {
            Map.Entry codeInfo = (Map.Entry) validationMessageSetIterator.next();
            if (code.equals(codeInfo.getKey().toString())) {
                HashMap messageAndFix = (HashMap) codeInfo.getValue();
                Set set = messageAndFix.entrySet();
                Iterator messageIterator = set.iterator();
                while (messageIterator.hasNext()) {
                    Map.Entry messageInfo = (Map.Entry) messageIterator.next();
                    if (messageInfo.getKey().toString().equals(code)) {
                        errorMessage = messageInfo.getValue().toString();
                    }
                }
            }

        }
        return errorMessage;
    }

    public String getFix(String code) {

        Set validationMessageSet = validationMessages().entrySet();
        Iterator validationMessageSetIterator = validationMessageSet.iterator();
        while (validationMessageSetIterator.hasNext()) {
            Map.Entry codeInfo = (Map.Entry) validationMessageSetIterator.next();
            if (code.equals(codeInfo.getKey().toString())) {
                HashMap messageAndFix = (HashMap) codeInfo.getValue();
                Set set = messageAndFix.entrySet();
                Iterator messageIterator = set.iterator();
                while (messageIterator.hasNext()) {
                    Map.Entry messageInfo = (Map.Entry) messageIterator.next();
                    if (messageInfo.getKey().toString().equals("fix" + code)) {
                        errorFixMethod = messageInfo.getValue().toString();

                    }
                }
            }

        }
        return errorFixMethod;
    }
}
