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
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.codec.binary.StringUtils;

/**
 *
 * @author paxterra
 */
class TAISyntaxValidator {
    HashMap paramFileErrorHash;
    HashMap paramFileWarnHash;
    HashMap paramFileInfoHash;
    // HashMap ospkErrorHash, ospkInfoHash, ospkWarnHash;
    HashMap<String, String> paramCaseTagHash = new HashMap<String, String>();
    String openCaseTag, closeCaseTag;
    String openCaseTagNumber, closeCaseTagNumber;
    String paramFileContent = "";
    String caseTagDetail;
    CodeEditorParams ContentParams;
    CodeEditor Content;
    HashMap ospkHashErrorCode = new HashMap();
    HashMap ospkHashWarnCode = new HashMap();
    HashMap ospkHashInfoCode = new HashMap();
    Matcher syntaxMatcher;
    ArrayList<String> errorCode = new ArrayList<String>();
    HashMap ospkErrorHash = new HashMap();
    HashMap ospkInfoHash = new HashMap();
    HashMap ospkWarnHash = new HashMap();
    HashMap tplFileErrorHash, tplFileWarnHash, tplFileInfoHash;
    ArrayList<String> errorValue = new ArrayList<String>();
    ArrayList<String> caseValue = new ArrayList<String>();

    public TAISyntaxValidator() {
    }

    public TAISyntaxValidator(CodeEditorParams paramEditor) {
        this.ContentParams = paramEditor;
    }

    public TAISyntaxValidator(CodeEditor paramEditor) {
        this.Content = paramEditor;
    }

    public void validatorParams(ArrayList<String> fileContent) {

        paramFileErrorHash = new HashMap();
        paramFileWarnHash = new HashMap();
        paramFileInfoHash = new HashMap();
        TAISyntaxMessage syntaxMessage = new TAISyntaxMessage();
        ArrayList<String> tagValue = new ArrayList<String>();
        
        for (int i = 0; i < fileContent.size(); i++) {
            syntaxValidator("^\\s*#", fileContent.get(i));
            Pattern blankSpace = Pattern.compile("^\\s+$");
            Matcher blankSpaceMatcher = blankSpace.matcher(fileContent.get(i));
            
            if (blankSpaceMatcher.find()){
                
            }
            if (!syntaxMatcher.find()) {
                syntaxValidator("\\<(.+)\\>", fileContent.get(i));
                if (syntaxMatcher.find()) {
                    Pattern sameLinePattern = Pattern.compile("\\<(.*)\\>(.*)\\<\\/(.*)\\>");
                    Matcher sameLineMatcher = sameLinePattern.matcher(syntaxMatcher.group());
                    if(sameLineMatcher.find()){
                                              
                        if (!syntaxMatcher.group(1).contains(">")){
                            paramFileErrorHash.put(i + 1, syntaxMessage.getMessage("param151"));
                        }
                        if (!syntaxMatcher.group().contains("<")){
                            paramFileErrorHash.put(i + 1, syntaxMessage.getMessage("param151"));
                        }
                        if(!sameLineMatcher.group(1).equals(sameLineMatcher.group(3))){
                            paramFileErrorHash.put(i + 1, syntaxMessage.getMessage("param151"));
                            
                        }else{

                        }
                        
                        Pattern startMatch = Pattern.compile("^\\<");
                        Matcher startMatcher = startMatch.matcher(syntaxMatcher.group());
                        
                        Pattern endMatch = Pattern.compile("\\>$");
                        Matcher endMatcher = endMatch.matcher(syntaxMatcher.group());
                        if (!startMatcher.find() ){
                          
                            paramFileErrorHash.put(i + 1, syntaxMessage.getMessage("param109"));
                        }
                        if ( !endMatcher.find()){
                            paramFileErrorHash.put(i + 1, syntaxMessage.getMessage("param113"));
                        }
                       
                    }else{
                        tagValue.add(syntaxMatcher.group(1));
                       
                    }
                    
                } else {
                    if (!fileContent.get(i).isEmpty()){
                         paramFileErrorHash.put(i + 1, syntaxMessage.getMessage("param113"));
                    }
            
                    
                }

                        Pattern blankSpaces = Pattern.compile("^\\s+$");
                        Matcher blankSpacesMatcher = blankSpaces.matcher(fileContent.get(i));
                
                        Pattern startMatch = Pattern.compile("^\\s*\\<");
                        Matcher startMatcher = startMatch.matcher(fileContent.get(i));
                        
                        Pattern endMatch = Pattern.compile("\\>\\s*$");
                        Matcher endMatcher = endMatch.matcher(fileContent.get(i));
                        if (startMatcher.find() && !fileContent.get(i).isEmpty()){
                            
                            
                        }else if (fileContent.get(i).isEmpty()) {
                           
                        }else{
                            
                            paramFileErrorHash.put(i + 1, syntaxMessage.getMessage("param109"));
                        }
                        if ( endMatcher.find() && !fileContent.get(i).isEmpty()){
                            
                        }else if (fileContent.get(i).isEmpty()){
                        }else {
                            
                            paramFileErrorHash.put(i + 1, syntaxMessage.getMessage("param111"));
                        }
                /*
                 * validation for <
                 */
                syntaxValidator("(.*)\\>", fileContent.get(i));
                if (syntaxMatcher.find()) {
                    syntaxValidator("\\<(.*)", syntaxMatcher.group(1));
                    if (!syntaxMatcher.find()) {
                        paramFileErrorHash.put(i + 1, syntaxMessage.getMessage("param109"));
                    }
                }


                /*
                 * end validation for <
                 */

                /*
                 * validation for > tag
                 */
                syntaxValidator("\\<(.+)", fileContent.get(i));
                if (syntaxMatcher.find()) {
                    syntaxValidator("\\w+(.+)>", syntaxMatcher.group(1));
                    if (!syntaxMatcher.find()) {
                        paramFileErrorHash.put(i + 1, syntaxMessage.getMessage("param112"));
                    }
                }


                /*
                 * End > validation
                 */

                /*
                 * Validation for log directory
                 */
                

                /*
                 * CASE info validation
                 */

                paramFileContent += fileContent.get(i) + "\n";
               
                syntaxValidator("\\<(.+)>", fileContent.get(i));
                if (syntaxMatcher.find()) {
                    Pattern endCasePattern = Pattern.compile("\\</CASE(\\d+)\\>");
                    Matcher endCaseMatch = endCasePattern.matcher(syntaxMatcher.group());
                    if (endCaseMatch.find()) {
                        closeCaseTagNumber = endCaseMatch.group(1);
                        closeCaseTag = endCaseMatch.group();
                        


                    } else {
                        Pattern openCasePattern = Pattern.compile("<CASE(\\d+)>");
                        Matcher openCaseMatch = openCasePattern.matcher(syntaxMatcher.group());
                        if (openCaseMatch.find()) {
                            openCaseTagNumber = openCaseMatch.group(1);
                            openCaseTag = openCaseMatch.group();
                        }
                    }
                }
            }



        }
        for (int i = 0; i < tagValue.size(); i++) {
            int flag = 0;
            for (int j = 0; j < tagValue.size(); j++) {
                if (("/" + tagValue.get(i)).equals(tagValue.get(j))) {
                    flag = 1;
                }
            }
            if (flag == 0) {
                syntaxValidator("\\/(.+)", tagValue.get(i));
                if (syntaxMatcher.matches() == true) {
                } else {
                    errorValue.add(tagValue.get(i));
                }
            }

        }
        for (int k = 0; k < errorValue.size(); k++) {
            String errortag = ("<" + errorValue.get(k) + ">");
            for (int ind = 0; ind < fileContent.size(); ind++) {
                if (errortag.equals(fileContent.get(ind).replaceFirst("\\s+", ""))) {
                    paramFileErrorHash.put(ind, syntaxMessage.getMessage("param100"));

                }
            }


        }



    }

    // ******************************validator subroutine ends
    // ***** function for OpenSpeak testscript (.ospk) validation starts from here
    public void ospkValidator(ArrayList<String> fileContent) {
        TAISyntaxMessage syntaxMessage = new TAISyntaxMessage();

        ArrayList<String> caseNumber = new ArrayList<String>();
        for (int i = 0; i < fileContent.size(); i++) {
            if (!fileContent.get(i).matches("\\s*")) {
                
                syntaxValidator("^\\s*(COMMENT|NAME|STEP|DESC|STEP|ON|ASSERT|LOG|INFO|WARN|DEBUG|END|CASE|STORE)\\s*(.+)", fileContent.get(i));
                if (!syntaxMatcher.find() && !fileContent.get(i).contains("=")) {
                    ospkErrorHash.put(i + 1, "illegal start of syntax");
                }
            }

            syntaxValidator("\\s*TEST\\s*NAME\\s*(.*)", fileContent.get(i));
            if (syntaxMatcher.find()) {
                if (syntaxMatcher.group(1).isEmpty()) {
                    ospkInfoHash.put(i + 1, syntaxMessage.getMessage("ospk601"));
                } else {
                    syntaxValidator("\\s*TEST(\\s*)*NAME\\s*\"(.*)\"", fileContent.get(i));
                    if (!syntaxMatcher.find()) {
                        ospkErrorHash.put(i + 1, syntaxMessage.getMessage("ospk501"));
                    }
                }
            }

            syntaxValidator("^\\s*CASE\\s+(.*)", fileContent.get(i));
            if (syntaxMatcher.find()) {
                
                if(!syntaxMatcher.group(1).isEmpty()){
                    if(!caseValue.contains(syntaxMatcher.group(1))){
                        
                        caseValue.add(syntaxMatcher.group(1));
                    }else if(caseValue.contains(syntaxMatcher.group(1))){
                        
                        ospkErrorHash.put(i+1, "Case already exists");
                    }
                    
                }else if (syntaxMatcher.group(1).isEmpty()){
                    
                    ospkErrorHash.put(i+1,"case number missing");
                }
            }
            
            syntaxValidator("^\\s*NAME\\s+(.*)", fileContent.get(i));
            if (syntaxMatcher.find()) {
                if (syntaxMatcher.group(1).isEmpty()) {
                    ospkInfoHash.put(i + 1, syntaxMessage.getMessage("ospk602"));
                } else {
                    Pattern commaPatternAtStart = Pattern.compile("^\"(.*)\"\\s*");
                    Matcher startMatcher = commaPatternAtStart.matcher(syntaxMatcher.group(1));
                    if(!startMatcher.find()){
                        ospkErrorHash.put(i+1, "invalid NAME statement");
                    }
                }
            }
            
            
            syntaxValidator("^\\s*STEP\\s+(.*)", fileContent.get(i));
            if (syntaxMatcher.find()) {
                if (syntaxMatcher.group(1).isEmpty()) {
                    ospkInfoHash.put(i + 1, syntaxMessage.getMessage("ospk602"));
                } else {
                    Pattern commaPatternAtStart = Pattern.compile("^\"(.*)\"\\s*");
                    Matcher startMatcher = commaPatternAtStart.matcher(syntaxMatcher.group(1));
                    if(!startMatcher.find()){
                        ospkErrorHash.put(i+1, "invalid STEP statement");
                    }
                }
            }

            syntaxValidator("^\\s*COMMENT\\s+(.*)", fileContent.get(i));
            if (syntaxMatcher.find()) {
                if (syntaxMatcher.group(1).isEmpty()) {
                    ospkInfoHash.put(i + 1, syntaxMessage.getMessage("ospk602"));
                } else {
                    Pattern commaPatternAtStart = Pattern.compile("^\"(.*)\"\\s*");
                    Matcher startMatcher = commaPatternAtStart.matcher(syntaxMatcher.group(1));
                    if(!startMatcher.find()){
                        ospkErrorHash.put(i+1, "invalid NAME statement");
                        
                    }
                }
            }
            
            
            syntaxValidator("^\\s*STORE\\s+(.*)\\s+IN\\s+(.*)", fileContent.get(i));
            if(syntaxMatcher.find()){
                syntaxValidator("^\\s*ON\\s+(\\w||\\d)+\\s+DO\\s+(.*)", syntaxMatcher.group(1));
                if(syntaxMatcher.find()){
                    OnDOMatching(syntaxMatcher.group(2), i);
                }
            }
            
            
            syntaxValidator("^\\s*ON\\s+(\\w||\\d)+\\s+DO\\s+(.*)", fileContent.get(i));
            if(syntaxMatcher.find()){
                OnDOMatching(syntaxMatcher.group(2), i);
            }
            
            syntaxValidator("^\\s*ASSERT\\s+(.*)\\s+(EQUALS|MATCHES|GREATER|LESSER|NOT EQUALS|NOT MATCHES|NOT GREATER|NOT LESSER)\\s+(.*)", fileContent.get(i));
            if (syntaxMatcher.find()) {
              
                
                syntaxValidator("\\s*(.*)\\s+ONPASS\\s+(.*)\\s+ONFAIL\\s+(.*)", syntaxMatcher.group(3));
                if (syntaxMatcher.find()) {
                    String onPassMessage = syntaxMatcher.group(2);
                    String onFailMessage = syntaxMatcher.group(3);
                    
                
                
                syntaxValidator("\\s*\"(.*)\"", onPassMessage);
                if (!syntaxMatcher.find()) {
                    ospkErrorHash.put(i + 1, syntaxMessage.getMessage("ospk518"));
                }
                syntaxValidator("\\s*\"(.*)\"", onFailMessage);
                if (!syntaxMatcher.find()) {
                    ospkErrorHash.put(i + 1, syntaxMessage.getMessage("ospk519"));
                }
           } else {
                ospkErrorHash.put(i + 1, syntaxMessage.getMessage("ospk520"));
            }
          }
        }

    }

//*********************************** end of ospk parsing function*********************


// **************** Verify Command sub routine starts here

    

    
    
    public void OnDOMatching(String line, int index){
        TAISyntaxMessage syntaxMessage = new TAISyntaxMessage();
        syntaxValidator("\\s*(.*)\\s+USING\\s+(.*)", line);
        
        if (syntaxMatcher.find()) {
            if (syntaxMatcher.group(1).isEmpty()) {
               ospkErrorHash.put(index + 1, syntaxMessage.getMessage("ospk509"));
            }
            if (syntaxMatcher.group(2).isEmpty()) {
                ospkErrorHash.put(index + 1, syntaxMessage.getMessage("ospk510"));
            }
            String argsWidComma = syntaxMatcher.group(2);
            Pattern moreArguments = Pattern.compile("(.*),(.*)");
            Matcher moreArgsMatch = moreArguments.matcher(syntaxMatcher.group(2));
            
            if (moreArgsMatch.find()){
                for(String argument : argsWidComma.split(",")){
                    Pattern asPattern = Pattern.compile("\\s*(.*)\\s+AS\\s+(.*)");
                    Pattern quotePattern = Pattern.compile("\\s*\"(.*)\"");
                    Pattern variablePattern = Pattern.compile("\\s*(\\w+)");
                    Matcher asMatcher = asPattern.matcher(argument);
                    Matcher quoteMatcher = quotePattern.matcher(argument);
                    Matcher variableMatcher = variablePattern.matcher(argument);
                    
                    if (asMatcher.find()){
                        
                    }else if (quoteMatcher.find()){
                        
                    }else if (variableMatcher.find()){
                        
                    }else{
                        ospkErrorHash.put(index, "Illegal type of arguments");
                    }
                }
            }
            
            if(!syntaxMatcher.group(2).contains(",")){
                Pattern asPattern = Pattern.compile("\\s*(.*)\\s+AS\\s+(.*)");
                    Pattern quotePattern = Pattern.compile("\\s*\"(.*)\"");
                    Pattern variablePattern = Pattern.compile("\\s*(\\w+)");
                    Matcher asMatcher = asPattern.matcher(syntaxMatcher.group(2));
                    Matcher quoteMatcher = quotePattern.matcher(syntaxMatcher.group(2));
                    Matcher variableMatcher = variablePattern.matcher(syntaxMatcher.group(2));
                    
                    if (asMatcher.find()){
                        
                    }else if (quoteMatcher.find()){
                        
                    }else if (variableMatcher.find()){
                        
                    }else{
                        ospkErrorHash.put(index, "Illegal type of arguments");
                    }
            }
            
            
        } else {
            syntaxValidator("^\\s*ON\\s*(.*)\\s*(DO|EXEC|CONFIG)\\s*(.*)\\s*USING\\s+(.*)$", line);
            if (syntaxMatcher.find()) {
            
                if (syntaxMatcher.group(1).isEmpty()) {
                    ospkErrorHash.put(index + 1, syntaxMessage.getMessage("ospk511"));
                }
                if (syntaxMatcher.group(2).isEmpty()) {
                    ospkErrorHash.put(index + 1, syntaxMessage.getMessage("ospk512"));
                }
                if (syntaxMatcher.group(3).isEmpty()) {
                    ospkErrorHash.put(index + 1, syntaxMessage.getMessage("ospk513"));
                }

                syntaxValidator("\\s*\\w+\\s+AS\\s+(.*)", syntaxMatcher.group(4));
                if (syntaxMatcher.find()) {
                    syntaxValidator("\\s*\\w+\\s+AS\\s+CASE\\[(.+)\\]", syntaxMatcher.group());
                    if (syntaxMatcher.find()) {
                        String[] caseParameterList = syntaxMatcher.group().split("\\,");
                        for (int j = 0; j < caseParameterList.length; j++) {
                            syntaxValidator("\\s*(\\w+)\\s+AS\\s+CASE\\[(.+)\\](.*)", caseParameterList[j]);
                            if (!syntaxMatcher.find()) {
                                ospkErrorHash.put(index + 1, syntaxMessage.getMessage("ospk514"));
                            }
                        }

                    }
                }
            }
        }

    }
    
    public void syntaxValidator(String regularExp, String line) {
        Pattern syntaxPattern = Pattern.compile(regularExp);
        syntaxMatcher = syntaxPattern.matcher(line);

    }

    public ArrayList<String> getErrorCode() {
        return errorCode;
    }
}
