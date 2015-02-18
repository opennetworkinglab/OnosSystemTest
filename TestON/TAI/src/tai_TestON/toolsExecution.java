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

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Locale;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Application;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.control.TextAreaBuilder;
import javafx.scene.control.TreeItem;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

/**
 *
 * @author paxterra
 */
public class toolsExecution extends Application{

    Scene scene;
    VBox baseBox;
    ComboBox<String> ConfigNameList,driverNameList;
    DriverTools toolsReference;
    GridPane selectionPane;
    TabPane consoleTabPane = new TabPane();
    Tab consoleTab = new Tab("Execution");
    int selectedTool= 0;
    Stage copyStage;
    HashMap<String,String> driverPathHash = new HashMap<>();
    TAILocale label = new TAILocale(Locale.ENGLISH);
    javafx.scene.control.TextArea executionConsole = TextAreaBuilder.create().build();
    
    public toolsExecution (int toolSelection){
        this.selectedTool = toolSelection;
    }
    
    @Override
    public void start(Stage primaryStage) throws Exception {
        copyStage = primaryStage;
        Group baseGroup = new Group();
        baseBox = new VBox(20);
        selectionPane = new GridPane();
        selectionPane.setPadding(new Insets(10, 30, 0, 20));
        Image testOn = new Image("/images/TestON.png",150,150,true,true);
        ImageView testOnImage = new ImageView(testOn);
        selectionPane.add(testOnImage, 4, 1);
        consoleTabPane.getTabs().addAll(consoleTab);
        baseBox.getChildren().addAll(selectionPane,consoleTabPane);
        executionConsole.setStyle(
                "-fx-text-fill: #0A0A2A;"
                + "-fx-background-color: #EFFBFB;");
        executionConsole.setEditable(false);
        consoleTab.setClosable(false);
        
        consoleTab.setContent(executionConsole);
        
        baseGroup.getChildren().addAll(baseBox);
        scene = new Scene(baseGroup, 500, 500);
         executionConsole.prefWidthProperty().bind(scene.widthProperty());
        executionConsole.prefHeightProperty().bind(scene.heightProperty());
        getSelectionArea();
        primaryStage.setScene(scene);
        primaryStage.show();
        
    }
    
    public void getSelectionArea(){
        ConfigNameList = new ComboBox<>();
        driverNameList = new ComboBox<>();
        Label driverNameLabel = new Label("Driver :");
        Label configNameLabel = new Label("Config :");
        
        Button run = new Button("Execute");
        Button cancel = new Button("Cancel");
        
        selectionPane.add(driverNameLabel, 0, 0);
        selectionPane.add(driverNameList, 1, 0);
        
        selectionPane.add(run, 0, 3);
        selectionPane.add(cancel, 2, 3);
        ObservableList<String> driverNames = driverNameList.getItems();
        Iterator<TreeItem<String>> driverIterator = toolsReference.driverExplorerTree.getChildren().iterator();
        while(driverIterator.hasNext()){
            TreeItem<String> treeItem = driverIterator.next();
            if(!treeItem.isLeaf()){
               Iterator<TreeItem<String>> innerIterator = treeItem.getChildren().iterator();
               while(innerIterator.hasNext()){
                   TreeItem<String> treeItem1 = innerIterator.next();
                   
                   if (treeItem1.isLeaf() && treeItem1.getValue().equals("fvtapidriver")){
                       String path = label.hierarchyTestON + "drivers/common/" + treeItem.getValue() + "/" + treeItem1.getValue();
                       driverPathHash.put("fvtapidriver", path);
                       driverNames.add("fvtapidriver");
                   }else if(!treeItem1.isLeaf()){
                       Iterator<TreeItem<String>> treeItemIter = treeItem1.getChildren().iterator();
                       while(treeItemIter.hasNext()){
                           TreeItem<String> treeItem2 = treeItemIter.next();
                           String path = label.hierarchyTestON + "drivers/common/" + treeItem.getValue() + "/" + treeItem1.getValue() + "/" + treeItem2.getValue(); 
                           driverNames.add(treeItem2.getValue());
                           driverPathHash.put(treeItem2.getValue(), path);
                       }
                   }
                   
                   
               }
            }
        }
        
        driverNameList.setItems(driverNames);
        
        cancel.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
                copyStage.close();
            }
        });
        
        run.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
                switch(selectedTool){
                    case 1:
                        try {
                           executionConsole.clear(); 
                          executeUpdateDriver();
                        } catch (IOException ex) {
                          Logger.getLogger(toolsExecution.class.getName()).log(Level.SEVERE, null, ex);
                        }
                        break;
                        
                     case 2 :
                        try {
                            executionConsole.clear();
                            executeGenerateDriver();
                        } catch (IOException ex) {
                            Logger.getLogger(toolsExecution.class.getName()).log(Level.SEVERE, null, ex);
                        }
                        
                }
            }
        });
        
    }
    
    public void executeUpdateDriver() throws IOException{
        
        ProcessBuilder builder = new ProcessBuilder(
            "/bin/sh", "-c", "cd "+ label.hierarchyTestON + "bin/" + "&& python cli.py updatedriver config " + label.hierarchyTestON + "/config/" + driverNameList.getSelectionModel().getSelectedItem().toString() +
                          ".cfg " + "drivers " + driverNameList.getSelectionModel().getSelectedItem().toString()  );
        builder.redirectErrorStream(true);
        Process p = builder.start();
        BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String line;
        while (true) {
            line = r.readLine();
            if (line == null) { break; }
            executionConsole.appendText("\n" + line);
        }
        
    }
    
    public void executeGenerateDriver() throws IOException{
       
        
        String driverToSpecify = driverPathHash.get(driverNameList.getSelectionModel().getSelectedItem()); 
        ProcessBuilder builder = new ProcessBuilder(
            "/bin/sh", "-c", "cd "+ label.hierarchyTestON + "bin/" + "&& python generatedriver.py " + driverNameList.getSelectionModel().getSelectedItem().toString()  );
        builder.redirectErrorStream(true);
        Process p = builder.start();
        BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String line;
        while (true) {
            line = r.readLine();
            if (line == null) { break; }
            executionConsole.appendText("\n" + line);
        }
        
    }
    
    public void setDriverToolsRef(DriverTools toolsRef){
        this.toolsReference = toolsRef;
    }
    
}
