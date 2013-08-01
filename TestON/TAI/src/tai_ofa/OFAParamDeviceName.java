/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

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
class OFAParamDeviceName {

    String paramFilePath;
    ArrayList<String> paramDeviceName;
    ArrayList<String> driverFunctionName;
    ArrayList<String> paramDeviceType;
    ArrayList<String> paramDeviceCoordinate;
    ArrayList<String> paramDeviceHost;
    ArrayList<String> paramDeviceUser;
    ArrayList<String> paramDevicePassword;
    ArrayList<String> paramDeviceTransport;
    ArrayList<String> paramDevicePort;
    ArrayList<String> paramDeviceBrowser;
    ArrayList<String> paramDeviceUrl;
    HashMap<String, String> deviceInfo = new HashMap();
    HashMap<String, String> urlInfo = new HashMap();
    HashMap<String, String> browserInfo = new HashMap();
    HashMap<String, String> coordinateInfo = new HashMap();
    HashMap<String, String> hostInfo = new HashMap();
    HashMap<String, String> userInfo = new HashMap();
    HashMap<String, String> passwordInfo = new HashMap();
    HashMap<String, String> portInfo = new HashMap();
    HashMap<String, String> transportInfo = new HashMap();
    String cliFunction;
    HashMap deviceFunctionAndParameter = new HashMap();
    HashMap<String, String> functionWithParameter;
    String functionName;
    String functionParameter;
    HashMap<String, String> webFunctionHashFirstParameter = new HashMap<String, String>();
    HashMap<String, String> webFunctionHashSecondParameter = new HashMap<String, String>();
    ArrayList<String> seleniumFunctionList = new ArrayList<String>();
    String bdrAction;
    TAILocale label = new TAILocale(new Locale("en", "EN"));
    String autoMateHarnessPath = label.OFAHarnessPath;
    ArrayList<String> bdrFunctionName;

    public OFAParamDeviceName() {
    }

    public OFAParamDeviceName(String filePath, String driverFilePath) {
        paramDeviceName = new ArrayList<String>();
        paramDeviceType = new ArrayList<String>();
        paramDeviceCoordinate = new ArrayList<String>();
        paramDeviceHost = new ArrayList<String>();
        paramDeviceUser = new ArrayList<String>();
        paramDevicePassword = new ArrayList<String>();
        paramDeviceTransport = new ArrayList<String>();
        paramDevicePort = new ArrayList<String>();
        paramDeviceBrowser = new ArrayList<String>();
        paramDeviceUrl = new ArrayList<String>();
        this.paramFilePath = filePath;
    }

    public void parseParamFile() {
        try {

            FileInputStream fstream = new FileInputStream(paramFilePath);
            ArrayList<String> paramFileName = new ArrayList<String>();
            ArrayList<String> nameBetweenTags = new ArrayList<String>();
            DataInputStream in = new DataInputStream(fstream);
            BufferedReader br = new BufferedReader(new InputStreamReader(in));
            String strLine;
            while ((strLine = br.readLine()) != null) {
                paramFileName.add(strLine);

            }

            for (int i = 0; i < paramFileName.size(); i++) {
                String dName = "";
                String dType = "";
                String dCoordinate = "";
                String dHost = "";
                String dUser = "";
                String dPassword = "";
                String dTransport = "";
                String dPort = "";
                String dBrowser = "";
                String dUrl = "";
                Pattern devicePatternMatch = Pattern.compile("<COMPONENT>");
                Matcher deviceNameMatch = devicePatternMatch.matcher(paramFileName.get(i));
                if (deviceNameMatch.find()) {
                    int j = i + 1;
                    while (!paramFileName.get(j).equals("</COMPONENT>")) {
                        Pattern newTag = Pattern.compile("<(.+)(\\d+)>");
                        Matcher tagMatch = newTag.matcher(paramFileName.get(j));
                        if (tagMatch.find()) {
                            String temp = tagMatch.group(1);
                            Pattern slashCheck = Pattern.compile("^\\w+");
                            Matcher slashMatch = slashCheck.matcher(temp);
                            if (slashMatch.find()) {
                                paramDeviceName.add(slashMatch.group() + tagMatch.group(2));
                                dName = slashMatch.group() + tagMatch.group(2);
                            }

                        }


                        Pattern deviceTypePattern = Pattern.compile("<type>\\s*(.+)\\s*</type>");
                        Matcher deviceTypeMatch = deviceTypePattern.matcher(paramFileName.get(j));

                        while (deviceTypeMatch.find()) {
                            paramDeviceType.add(deviceTypeMatch.group(1));
                            dType = deviceTypeMatch.group(1).toLowerCase();

                        }
                        Pattern deviceCoordinatePattern = Pattern.compile("<coordinate(x,y)>\\s*(.+)\\s*</coordinate(x,y)>");
                        Matcher deviceCoordinateMatch = deviceCoordinatePattern.matcher(paramFileName.get(j));
                        while (deviceCoordinateMatch.find()) {
                            paramDeviceCoordinate.add(deviceCoordinateMatch.group(1));
                            dCoordinate = deviceCoordinateMatch.group(1);

                        }
                        Pattern devicehostNamePattern = Pattern.compile("<host>\\s*(.+)\\s*</host>");
                        Matcher deviceHostMatch = devicehostNamePattern.matcher(paramFileName.get(j));

                        while (deviceHostMatch.find()) {
                            paramDeviceHost.add(deviceHostMatch.group(1));
                            dHost = deviceHostMatch.group(1);
                        }
                        Pattern deviceUserPattern = Pattern.compile("<user>\\s*(.+)\\s*</user>");
                        Matcher deviceUserMatch = deviceUserPattern.matcher(paramFileName.get(j));
                        while (deviceUserMatch.find()) {
                            paramDeviceUser.add(deviceUserMatch.group(1));
                            dUser = deviceUserMatch.group(1);
                        }

                        Pattern devicePasswordPattern = Pattern.compile("<password>\\s*(.+)\\s*</password>");
                        Matcher devicePasswordMatch = devicePasswordPattern.matcher(paramFileName.get(j));
                        while (devicePasswordMatch.find()) {
                            paramDevicePassword.add(devicePasswordMatch.group(1));
                            dPassword = devicePasswordMatch.group(1);
                        }

                        Pattern devicePortPattern = Pattern.compile("<test_target>\\s*(.+)\\s*</test_target>");
                        Matcher devicePortMatch = devicePortPattern.matcher(paramFileName.get(j));
                        while (devicePortMatch.find()) {
                            paramDevicePort.add(devicePortMatch.group(1));
                            dPort = devicePortMatch.group(1);
                        }

                        deviceInfo.put(dName, dType);
                        coordinateInfo.put(dName, dCoordinate);
                        hostInfo.put(dName, dHost);
                        userInfo.put(dName, dUser);
                        passwordInfo.put(dName, dPassword);
                        portInfo.put(dName, dPort);
                        j++;
                    }
                }
            }
            //Close the input stream
            in.close();
        } catch (Exception e) {//Catch exception if any
            System.err.println("Error: " + e.getMessage());
        }
    }

    public void parseDevice(String devicePath) {
        try {
            FileInputStream fstream = new FileInputStream(devicePath);
            DataInputStream in = new DataInputStream(fstream);
            BufferedReader br = new BufferedReader(new InputStreamReader(in));
            String strLine;
            while ((strLine = br.readLine()) != null) {
                Pattern cliFunctionPattern = Pattern.compile("sub\\s+(\\w+)");
                Matcher cliFunctionMatch = cliFunctionPattern.matcher(strLine);
                Pattern cliFunctionArgumentPattern = Pattern.compile("utilities.parse_args\\(\\[\\s+qw\\((.*)\\)\\s*\\]\\,(.*)");
                Matcher argumentMatch = cliFunctionArgumentPattern.matcher(strLine);
                while (cliFunctionMatch.find()) {
                    cliFunction = cliFunctionMatch.group(1);
                    Pattern rm = Pattern.compile("_(.*)");
                    Matcher str2 = rm.matcher(cliFunction);
                    if (!str2.find()) {
                    }
                }
                while (argumentMatch.find()) {
                    deviceFunctionAndParameter.put(cliFunction, argumentMatch.group(1));
                }
            }
        } catch (Exception e) {
        }
    }

    public void driverFunctionName(String driverPath) {
        try {
            functionWithParameter = new HashMap<String, String>();
            FileInputStream fstream = new FileInputStream(driverPath);
            driverFunctionName = new ArrayList<String>();
            DataInputStream in = new DataInputStream(fstream);
            BufferedReader br = new BufferedReader(new InputStreamReader(in));
            String strLine;
            while ((strLine = br.readLine()) != null) {
                Pattern functionParameterPattern = Pattern.compile("(.*)\\s*=\\s*utilities.parse_args\\(\\s*\\[\\s*(.*)\\s*\\]\\s*\\,(.*)");
                Matcher functionParaMeterMatch = functionParameterPattern.matcher(strLine);
                Pattern pattern = Pattern.compile("^\\s*def\\s+(\\w+)");
                Matcher match = pattern.matcher(strLine);
                while (match.find()) {
                    functionName = match.group(1);
                    Pattern cliFunctionWithOut_ = Pattern.compile("_(.*)");
                    Matcher cliFunctionWithOut_Match = cliFunctionWithOut_.matcher(functionName);
                    if (!cliFunctionWithOut_Match.find()) {
                        driverFunctionName.add(match.group(1));
                    }


                }
                while (functionParaMeterMatch.find()) {
                    functionParameter = functionParaMeterMatch.group(2);
                    functionWithParameter.put(functionName, functionParameter);
                }
            }
        } catch (Exception e) {
        }
    }

    public ArrayList<String> getParamDeviceName() {
        return paramDeviceName;
    }

    public ArrayList<String> getParamDeviceType() {
        return paramDeviceType;
    }

    public ArrayList<String> getDriverFunctionName() {
        return driverFunctionName;
    }

    public ArrayList<String> getCoordinateName() {
        return paramDeviceCoordinate;
    }

    public ArrayList<String> getBrowserName() {
        return paramDeviceBrowser;
    }

    public ArrayList<String> getHostName() {
        return paramDeviceHost;
    }

    public ArrayList<String> getUserName() {
        return paramDeviceUser;
    }

    public ArrayList<String> getPassword() {
        return paramDevicePassword;
    }

    public ArrayList<String> getTransport() {
        return paramDeviceTransport;
    }

    public ArrayList<String> getPort() {
        return paramDevicePort;
    }

    public ArrayList<String> getUrl() {
        return paramDeviceUrl;
    }

    public HashMap<String, String> getdeviceNameAndType() {
        return deviceInfo;
    }

    public HashMap<String, String> getdeviceNameAndBrowser() {
        return browserInfo;
    }

    public HashMap<String, String> getdeviceNameAndUrl() {
        return urlInfo;
    }

    public HashMap<String, String> getdeviceNameAndCoordinate() {
        return coordinateInfo;
    }

    public HashMap<String, String> getdeviceNameAndHost() {
        return hostInfo;
    }

    public HashMap<String, String> getdeviceNameAndUser() {
        return userInfo;
    }

    public HashMap<String, String> getdeviceNameAndPassword() {
        return passwordInfo;
    }

    public HashMap<String, String> getdeviceNameAndTransport() {
        return transportInfo;
    }

    public HashMap<String, String> getdeviceNameAndPort() {
        return portInfo;
    }

    public HashMap<String, String> getDeviceFunctionAndArgument() {
        return deviceFunctionAndParameter;
    }
}
