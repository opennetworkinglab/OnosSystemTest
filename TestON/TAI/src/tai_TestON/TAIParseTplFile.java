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

import com.sun.applet2.AppletParameters;
import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import java.util.Vector;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.apache.commons.codec.binary.StringUtils;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FileUtils;
import org.apache.xmlrpc.XmlRpcClient;
import org.apache.xmlrpc.XmlRpcException;

/**
 *
 * @author paxterra
 */
class TAIParseTplFile {
   

  public Hashtable parseTpl(String fileName, String deviceName, String deviceTypeParent) {

       Hashtable returnHash = new Hashtable();    
        Hashtable resultXmlServer = new Hashtable();     
        XmlRpcClient server = null;
        Vector params = new Vector();
        params.add(new String(fileName));
        try {
               server = new XmlRpcClient("http://localhost:9000");
               try {
                     resultXmlServer = (Hashtable) server.execute("getDict", params);
               } catch (XmlRpcException ex) {
                     Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
               } catch (IOException ex) {
                     Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
               }
         } catch (MalformedURLException ex) {
               Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
         }
    
    
        Hashtable componentHash = new Hashtable();
        componentHash = (Hashtable) resultXmlServer.get("TOPOLOGY");
        
         
        Hashtable deviceHash =  new Hashtable<>();
        deviceHash = (Hashtable) componentHash.get("COMPONENT");
        
        Hashtable deviceNameHash = new Hashtable();
        deviceNameHash = (Hashtable) deviceHash.get(deviceName);
        
        returnHash = (Hashtable) deviceNameHash.get("COMPONENTS");
        return returnHash;

    }

    public Hashtable parseLinkTpl(String fileName, String name) {
        Hashtable returnHash = new Hashtable();    
        Hashtable resultXmlServer = new Hashtable();     
        XmlRpcClient server = null;
        Vector params = new Vector();
        params.add(new String(fileName));
        try {
               server = new XmlRpcClient("http://localhost:9000");
               try {
                     resultXmlServer = (Hashtable) server.execute("getDict", params);
               } catch (XmlRpcException ex) {
                     Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
               } catch (IOException ex) {
                     Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
               }
         } catch (MalformedURLException ex) {
               Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
         }
    
    
        Hashtable componentHash = new Hashtable();
        componentHash = (Hashtable) resultXmlServer.get("TOPOLOGY");
      
         
        Hashtable deviceHash =  new Hashtable<>();
        deviceHash = (Hashtable) componentHash.get("COMPONENT");
       
        if(componentHash.get("COMPONENT") instanceof Hashtable){
            
        }
        
        returnHash =  (Hashtable) deviceHash.get(name); 
       
        
      
    
        return returnHash;
    }
    
   public Hashtable getDeviceHash(String fileName){
       Hashtable returnHash = new Hashtable();    
        Hashtable resultXmlServer = new Hashtable();     
        XmlRpcClient server = null;
        Vector params = new Vector();
        params.add(new String(fileName));
        try {
               server = new XmlRpcClient("http://localhost:9000");
               try {
                     resultXmlServer = (Hashtable) server.execute("getDict", params);
               } catch (XmlRpcException ex) {
                     Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
               } catch (IOException ex) {
                     Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
               }
         } catch (MalformedURLException ex) {
               Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
         }
    
    
        Hashtable componentHash = new Hashtable();
        componentHash = (Hashtable) resultXmlServer.get("TOPOLOGY");
     
         
        Hashtable deviceHash =  new Hashtable<>();
        deviceHash = (Hashtable) componentHash.get("COMPONENT");
        
        return deviceHash;
   }
    
    
}
