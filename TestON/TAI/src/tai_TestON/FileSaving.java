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

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Locale;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javafx.application.Application;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.TextAreaBuilder;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;
import javafx.stage.Stage;

/**
 *
 * @author paxterra
 */
public class FileSaving extends Application {

    Scene scene;
    javafx.scene.control.TextArea fileText = TextAreaBuilder.create().build();
    Button save,cancel;
    HashMap<String,String> addedStatmentHash = new HashMap<>();
    TAIFileOperations fileOperation = new TAIFileOperations();
    TAILocale label = new TAILocale(Locale.ENGLISH);
    String testName,outputString,stepCounter,expectedStep;
    int stepCount = 0;
    String filePath;
    
    /**
     *
     * @param addedStatments
     */
    public FileSaving(HashMap<String,String> addedStatments,String fileName){
        this.addedStatmentHash = addedStatments;
        testName = fileName;
    }
    
    @Override
    public void start(final Stage primaryStage) throws Exception {
        Group baseGroup = new Group();
        VBox baseBox = new VBox(20);
        Text title = new Text("The newly modified file :");
        
        HBox buttonBox = new HBox(30);
        save = new Button("Save");
        cancel = new Button("Don't Save");
        
        
        
        buttonBox.getChildren().addAll(save,cancel);
        
       baseBox.getChildren().addAll(title,fileText,buttonBox);
       
       baseGroup.getChildren().addAll(baseBox);
       
       scene = new Scene(baseGroup,500,500);
       
       save.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
               try {
                   fileOperation.saveFile(new File(filePath), outputString);
               } catch (FileNotFoundException ex) {
                   Logger.getLogger(FileSaving.class.getName()).log(Level.SEVERE, null, ex);
               } catch (IOException ex) {
                   Logger.getLogger(FileSaving.class.getName()).log(Level.SEVERE, null, ex);
               }
               primaryStage.close();
            }
        });
       
       
       cancel.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
               primaryStage.close();
            }
        });
       
       
        fileText.prefHeightProperty().bind(scene.heightProperty().subtract(100));
        fileText.prefWidthProperty().bind(scene.widthProperty().subtract(5));
        getContent();
        primaryStage.setTitle("Modified Test Script");
       primaryStage.setScene(scene);
        primaryStage.show();
       
        
    }
    
    
    
    public void getContent(){
        outputString = "";
        filePath = label.hierarchyTestON + "/tests/" + testName + "/" + testName + ".ospk";
        //fileText.setText(fileOperation.getContents(new File(filePath)));
        String content = fileOperation.getContents(new File(filePath));
        String[] fileContent = content.split("\n");        
        for (int i = 0; i < fileContent.length; i++) {
                Pattern casePattern = Pattern.compile("\\s*CASE\\s*(\\d+)\\s*");
                Matcher caseMatcher = casePattern.matcher(fileContent[i]);
                if (caseMatcher.find()) {
                    String caseNumber = caseMatcher.group(1);
                    outputString = outputString + "\n" + fileContent[i];
                    i++;
                    while(i<fileContent.length){
                        Pattern casesPatterns = Pattern.compile("\\s*CASE\\s*(\\d+)\\s*");
                            Matcher casesMatchers = casesPatterns.matcher(fileContent[i]);
                            if (casesMatchers.find()) {
                                break;
                            } else {
                                Pattern stepPattern = Pattern.compile("\\s*STEP\\s+\"\\s*(.*)\\s*\"\\s*");
                                Matcher stepMatcher = stepPattern.matcher(fileContent[i]);
                                try {
                                    if (stepMatcher.find()) {
                                        stepCount++;
                                        stepCounter = caseNumber + "." + String.valueOf(stepCount);
                                        if(addedStatmentHash.containsKey(stepCounter)){
                                            expectedStep = caseNumber + "." + String.valueOf(stepCount + 1);
                                            outputString = outputString + "\n" + fileContent[i];
                                        }else{
                                            if(expectedStep.equals(stepCounter)){
                                                outputString = outputString + "\n" + addedStatmentHash.get(caseNumber + "." + String.valueOf(stepCount - 1));
                                                outputString = outputString + "\n" + fileContent[i];
                                            }else {
                                                outputString = outputString + "\n" + fileContent[i];
                                            }
                                        }
                                        
                                        
                                        
                                    }else {
                                        outputString = outputString + "\n" + fileContent[i];
                                    }
                                } catch (Exception e) {
                                    break;
                                }
                                i++;
                            }    
                    }
                    i--;
                }else {
                    outputString = outputString + "\n" + fileContent[i];
                }
            }
        
        fileText.setText(outputString);
        
    }
    
}
