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

import com.sun.javafx.scene.control.skin.PaginationSkin;
import com.sun.media.jfxmedia.events.NewFrameEvent;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Locale;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Application;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.Event;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.geometry.Orientation;
import javafx.scene.Group;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.control.Accordion;
import javafx.scene.control.Button;
import javafx.scene.control.ContextMenu;
import javafx.scene.control.Label;
import javafx.scene.control.Menu;
import javafx.scene.control.MenuItem;
import javafx.scene.control.SplitPane;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.TextField;
import javafx.scene.control.TextFieldBuilder;
import javafx.scene.control.TitledPane;
import javafx.scene.control.ToolBar;
import javafx.scene.control.Tooltip;
import javafx.scene.control.TreeItem;
import javafx.scene.control.TreeView;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.control.cell.TextFieldTableCell;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.input.InputEvent;
import javafx.scene.input.KeyEvent;
import javafx.scene.input.MouseButton;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Pane;
import javafx.scene.layout.TilePane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.text.Font;
import javafx.scene.text.Text;
import javafx.stage.FileChooser;
import javafx.stage.Stage;

/**
 *
 * @author Deepak Mishra
 */
public class DriverTools extends Application{

    Scene scene;
    Stage primaryStage ;
    int toolSelection;
    VBox foundationPane,box,buttonTableVBox;
    ToolBar toolsBar;
    TabPane explorer;
    TabPane editor ;
    Tab explorerTab;
    Tab editorTab;
    double toolBarHeight;
    Accordion explorerCollection;
    TitledPane configExplorer,logExplorer,driverExplorer;
    String projectWorkSpacePath;
    TAILocale label = new TAILocale(new Locale("en", "EN"));
    TreeItem<String> configExplorerTree, logExplorerTree;
    TreeView<String> configExplorerTreeView, logExplorerTreeView;
    SplitPane editorBasePane = new SplitPane();
    TAIFileOperations fileOperation = new TAIFileOperations(); 
    ContextMenu contextMenu;
    TreeItem device,driverExplorerTree;
    Button run,save;
    FileChooser open;
    
    
    Text Heading;
    TreeView<String> driverExplorerTreeView;
    DriverTools toolsReference;
    public  DriverTools(int caseNumber){
        
        this.toolSelection = caseNumber;
        toolsReference = this ;
        
    }
    
    
    
    @Override
    public void start(Stage stage) throws Exception {
        primaryStage = stage;
        
        Group rootGroup = new Group();
        
        foundationPane = new VBox();
        scene = new Scene(rootGroup, 800,600);
        buttonTableVBox = new VBox();
        getToolBar();
        toolsBar.setMinHeight(scene.heightProperty().get() / 20);
        toolsBar.prefWidthProperty().bind(scene.widthProperty());
        toolBarHeight = toolsBar.getMinHeight();
        explorerTab = new Tab("Explorer");
        editorTab = new Tab("Config");
        explorerCollection = new Accordion();
        
        Pane tabPaneBox = new Pane();
       
        explorer = new TabPane();  
        editor = new TabPane();
     
        explorer.setLayoutX(0);
        explorer.prefHeightProperty().bind(scene.heightProperty().subtract(toolBarHeight +  1));
        explorer.setMinWidth(200);
        explorer.getTabs().add(explorerTab);
        
      
        editor.setLayoutX(210);
        editor.prefHeightProperty().bind(scene.heightProperty().subtract(toolBarHeight +  1));
        editor.prefWidthProperty().bind(scene.widthProperty());
        explorer.prefHeightProperty().bind(scene.heightProperty());
        tabPaneBox.setMinHeight(scene.heightProperty().subtract(toolsBar.heightProperty().get()).get());
        tabPaneBox.getChildren().addAll(explorer,editor);
        foundationPane.getChildren().addAll(toolsBar,tabPaneBox);
        getToolInterface();
        rootGroup.getChildren().addAll(foundationPane);
        
        stage.setTitle("TestON - Automation is O{pe}N");
        stage.setScene(scene);
        stage.setResizable(true);
        stage.sizeToScene();
        stage.show();
        
        
    }
    
    
    
    public void getToolInterface(){
        
       switch(toolSelection){
           case 1:
              
               getDriverExplorer();
               explorerTab.setContent(explorerCollection);
               getConfigEditor(toolSelection);
               explorerCollection.getPanes().add(driverExplorer);
               break;
           case 2:
               getDriverExplorer();
               getLogExplorer();
               
               explorerTab.setContent(explorerCollection);
               getConfigEditor(toolSelection);
               explorerCollection.getPanes().add(driverExplorer);
               break;
       }
       
        run.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
              
                toolsExecution execution = new toolsExecution(toolSelection);
                execution.setDriverToolsRef(toolsReference);
                try {
                    execution.start(new Stage());
                } catch (Exception ex) {
                    Logger.getLogger(DriverTools.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        });
    }
    
    
    public void getConfigEditor(int caseNumber){
        
       
        HBox buttonBox = new HBox(30);
        Button saveConfigTree = new Button("Save");
        Button deleteConfigTree = new Button("Delete");
        Button addDevice = new Button("Add");
        buttonBox.getChildren().addAll(saveConfigTree,addDevice,deleteConfigTree);
        
        
        switch(caseNumber){
            case 1:
               break;
            case 2:
               
                break;
                
        }
        
  
        editorTab.setContent(editorBasePane);
    }
    

    
    public void getconfigExplorer(){
        
        projectWorkSpacePath = label.hierarchyTestON  + "/config/"; 
        
        
        File[] file = File.listRoots();
        Path name = new File(projectWorkSpacePath).toPath();
        LoadConfigDirectory treeNode = new LoadConfigDirectory(name);
        treeNode.setExpanded(true);
        configExplorerTree = treeNode;

        
        
        
    }
    
    public void getLogExplorer(){
        
        projectWorkSpacePath = label.hierarchyTestON  + "/bin/"; 
        logExplorer = new TitledPane();
        logExplorer.setText("Log Explorer");
        
        
        File[] file = File.listRoots();
        Path name = new File(projectWorkSpacePath).toPath();
        LoadConfigDirectory treeNode = new LoadConfigDirectory(name);
        treeNode.setExpanded(true);
        
        logExplorerTreeView = new TreeView<String>(treeNode);
        logExplorerTreeView.setShowRoot(false);
        
        VBox logExplBox = new VBox();
        Button newTest = new Button("Refresh");
        logExplorerTreeView.setMinHeight(scene.getHeight() - (40 + toolBarHeight ));
        logExplBox.getChildren().addAll(newTest, logExplorerTreeView);
        
        logExplorer.setContent(logExplBox);
        
        
        explorerCollection.getPanes().addAll(logExplorer);
    }
    
    public void getToolBar(){
        toolsBar = new ToolBar();
        
        Image folderImage = new Image("images/New123.png",20.0,20.0, true, true);
        Button newFile = new Button("", new ImageView(folderImage));
        newFile.setTooltip(new Tooltip("New"));
        
        newFile.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
                NewDriverGeneration newDriver = new NewDriverGeneration(toolsReference);
                try {
                    newDriver.start(new Stage());
                } catch (Exception ex) {
                    Logger.getLogger(DriverTools.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        });
        Image openFile1 = new Image("images/open.png",20.0,20.0, true, true);
        Button openFile = new Button("", new ImageView(openFile1));
        openFile.setTooltip(new Tooltip("Open"));
        
        openFile.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
                openFile("cfg", "");
            }
        });
        
        Image saveImage = new Image("images/save.png",20.0,20.0, true, true);
        save  = new Button("", new ImageView(saveImage));
        save.setTooltip(new Tooltip("Save"));
        
        Image playImage = new Image("images/playImg.jpg",20.0,20.0, true, true);
        run  = new Button("", new ImageView(playImage));
        run.setTooltip(new Tooltip("Run"));
        
        toolsBar.getItems().addAll(newFile,openFile,save,run);

    }
    
    public void tabEditor(final ToolsEditor Content, final String title, String str) {
    
        

        final Tab editorTab = new Tab();   
        final File fileName;
        ObservableList<Tab> allTab = editor.getTabs();
        if (allTab.isEmpty()) {
            String fname = "";
            String ext = "";
            int mid = title.lastIndexOf(".");
            fname = title.substring(0, mid);
            ext = title.substring(mid + 1, title.length());

            if ("cfg".equals(ext) || "py".equals(ext) || "log".equals(ext)) {

                Content.prefWidthProperty().bind(scene.widthProperty().subtract(270));

                fileName = new File(title);
                editorTab.setText(fileName.getName());
            
                
                editorTab.setContent(Content);
                editorTab.setId(title);
                String currentTab1 = editorTab.getId();
               
                editor.getTabs().add(editorTab);
                //editorTabPane.prefWidth(scene.widthProperty().get()-900);
                
                javafx.scene.control.SingleSelectionModel<Tab> selectionModel = editor.getSelectionModel();
                selectionModel.select(editorTab);
                Content.setOnKeyReleased(new EventHandler<InputEvent>() {

                    @Override
                    public void handle(InputEvent arg0) {
                        
                    }
                });
            
                save.setOnAction(new EventHandler<ActionEvent>() {
                                    @Override
                                    public void handle(ActionEvent arg0) {

                                        javafx.scene.control.SingleSelectionModel<Tab> selectionModel = editor.getSelectionModel();
                                        String currentTab1 = selectionModel.getSelectedItem().getId();

                                        selectionModel.getSelectedItem().setText(fileName.getName());
                                        String currentFileContent = Content.getCodeAndSnapshot();
                                        try {
                                             if(fileName.exists()){
                                                fileOperation.saveFile(fileName, currentFileContent);
                                            }else{
                                               fileName.createNewFile();
                                               fileOperation.saveFile(fileName, currentFileContent);
                                            }
                                       
                                        } catch (FileNotFoundException ex) {
                                            Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
                                        } catch (IOException ex) {
                                            Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
                                        }

                                    }
                                });  
                
            }
        } else {
                boolean tabexistsFlag = false;
            for (Tab tab : allTab) {
                if (tab.getId().equals(title)) {
                    javafx.scene.control.SingleSelectionModel<Tab> selectionModel = editor.getSelectionModel();
                    selectionModel.select(tab);
                    tabexistsFlag = true;
                    break;
                } else {
                }
            }
            if (tabexistsFlag == false) {
                
                String fname = "";
                String ext = "";
                int mid = title.lastIndexOf(".");
                fname = title.substring(0, mid);
                ext = title.substring(mid + 1, title.length());
                
                if ("cfg".equals(ext) || "py".equals(ext) || "log".equals(ext)) {

                Content.prefWidthProperty().bind(scene.widthProperty().subtract(500));

                fileName = new File(title);
                editorTab.setText(fileName.getName());
              
                
                editorTab.setContent(Content);
                editorTab.setId(title);
                String currentTab1 = editorTab.getId();
               
                editor.getTabs().add(editorTab);
              
                
                javafx.scene.control.SingleSelectionModel<Tab> selectionModel = editor.getSelectionModel();
                selectionModel.select(editorTab);
                Content.setOnKeyReleased(new EventHandler<InputEvent>() {

                    @Override
                    public void handle(InputEvent arg0) {
                        
                    }
                });
                
                save.setOnAction(new EventHandler<ActionEvent>() {
                                    @Override
                                    public void handle(ActionEvent arg0) {

                                        javafx.scene.control.SingleSelectionModel<Tab> selectionModel = editor.getSelectionModel();
                                        String currentTab1 = selectionModel.getSelectedItem().getId();

                                        selectionModel.getSelectedItem().setText(fileName.getName());
                                        String currentFileContent = Content.getCodeAndSnapshot();
                                        try {
                                            
                                            if(fileName.exists()){
                                                fileOperation.saveFile(fileName, currentFileContent);
                                            }else{
                                               fileName.createNewFile();
                                               fileOperation.saveFile(fileName, currentFileContent);
                                            }
                                            
                                        } catch (FileNotFoundException ex) {
                                            Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
                                        } catch (IOException ex) {
                                            Logger.getLogger(TAI_TestON.class.getName()).log(Level.SEVERE, null, ex);
                                        }

                                    }
                                });
              }       
           }
        }
        
        
        editorTab.setOnSelectionChanged(new EventHandler<Event>() {

            @Override
            public void handle(Event t) {
                
            }
        });
        
        
        
        
        

    }
    
 public void getDriverExplorer() {

        projectWorkSpacePath = label.hierarchyTestON + "/drivers/common";

        final Node rootIcon = new ImageView(new Image(getClass().getResourceAsStream("/images/project.jpeg"), 16, 16, true, true));
        driverExplorerTree = new TreeItem<String>("Drivers");
        File[] file = File.listRoots();

        Path name = new File(projectWorkSpacePath).toPath();
        TAILoadTree treeNode = new TAILoadTree(name);

        driverExplorerTree.setExpanded(true);
        //create the tree view
        driverExplorerTree = treeNode;
        driverExplorerTreeView = new TreeView<String>(treeNode);
        driverExplorer = new TitledPane("Driver Explorer", driverExplorerTreeView);

        driverExplorer.prefHeight(scene.heightProperty().get());

        VBox driverExpl = new VBox();
        driverExpl.getChildren().addAll(new Button("New Driver"), driverExplorerTreeView);
        driverExplorerTreeView.setShowRoot(false);
        driverExplorerTreeView.setMinHeight(scene.getHeight() - (toolBarHeight + 50));

        driverExplorer.setContent(driverExpl);
        driverExplorer.prefHeight(scene.heightProperty().get());


        ObservableList<TreeItem<String>> children = driverExplorerTree.getChildren();
        Iterator<TreeItem<String>> tree = children.iterator();
        while (tree.hasNext()) {
            TreeItem<String> value = tree.next();
            if (value.getValue().equals("common")) {
                driverExplorerTreeView.setShowRoot(false);
            }
        }

        driverExplorerTreeView.setOnMouseClicked(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent event) {

                if (event.getClickCount() == 2 && event.getButton() == MouseButton.PRIMARY) {
                    //final Node rootIcon = new ImageView(new Image(getClass().getResourceAsStream("/images/project.jpeg")));
                    TreeItem<String> driverSelectedItem = driverExplorerTreeView.getSelectionModel().getSelectedItem();
                    getConfig(driverSelectedItem.getValue());
                    
                }else if (event.getClickCount() == 1 && event.getButton() == MouseButton.SECONDARY){
                    contextMenu();
                    contextMenu.show(driverExplorerTreeView, event.getScreenX(), event.getScreenY());
                }
            }
        });



        driverExplorerTreeView.getSelectionModel().selectedItemProperty().addListener(new ChangeListener() {
            @Override
            public void changed(ObservableValue observable, Object oldValus, Object newValue) {
                
            }
        });

        driverExplorerTree.setExpanded(true);
        
        
    }
 
 public void getConfig(String driverName){
     String workSpaceConfig = label.hierarchyTestON + "/config/";
     File path = new File(workSpaceConfig + driverName + ".cfg");
     String driverPath = getDriverPath();
     String generateDriverContent = "<device>\n" + "\t<" + driverName + ">\n" + "\t\t<user_name> openflow </user_name>\n" + "\t\t<ip_address>192.168.56.101</ip_address>\n" +
                                    "\t\t<password>openflow</password>\n" + "\t\t<help_keyword> ? </help_keyword>\n" + "\t\t<interrupt_key> C </interrupt_key>\n" + 
                                    "\t\t<command_search_regex> \"\" </command_search_regex>\n" + "\t\t<command> \'show interfaces, set interfaces ethernet \'</command>\n" + 
                                    "\t\t<end_pattern> Enter </end_pattern>\n" + "\t</" + driverName + ">\n" + "</device>";
     
     String updateDriverContent = "<config-driver>\n" + "\t<importTypes>\n" + "\t\t<" + driverName + ">\n" + "\t\t\t<driver-path>"+ driverPath + "</driver-path>\n" +"\t\t\t<modules>\n" + "\t\t\t\t<module1>\n" +
                                  "\t\t\t\t\t<name> moduleName </name>\n" + "\t\t\t\t\t<path>" + label.hierarchyTestON +"/lib/flowvisor-test/test/testUtils" + "</path>\n" +
                                  "\t\t\t\t\t<set-path>" + label.hierarchyTestON + "/lib/flowvisor-test/src/python" + "</set-path>\n" + "\t\t\t\t\t<methods>\n" +
                                  "\t\t\t\t\t\t<ignore-list> tearDownFakeDevices,chkSwitchStats</ignore-list>\n" + "\t\t\t\t\t\t<add-list> chkSetUpCondition </add-list>\n" +
                                  "\t\t\t\t\t</methods>\n" + "\t\t\t\t</module1>\n" + "\t\t\t</modules>\n" +  "\t\t</" + driverName + ">\n" + "\t</importTypes>\n" + "</config-driver>";
     
     
     if(path.exists()){
         String fileContent = fileOperation.getContents(path);
         switch(toolSelection) {
             case 1:
                 if(fileContent.startsWith("<config-driver>")){
                   tabEditor(new ToolsEditor(fileContent),  path.toString(), driverName);
                 }else {
                    tabEditor(new ToolsEditor(updateDriverContent),  path.toString(), driverName); 
                 }
                 break;
             case 2:
                 if(fileContent.startsWith("<device>")){
                   tabEditor(new ToolsEditor(fileContent),  path.toString(), driverName);
                 }else {
                    tabEditor(new ToolsEditor(generateDriverContent),  path.toString(), driverName); 
                 }
                 break;
         }
         
     }else if (!path.exists()){
         switch (toolSelection){
             case 1 :
                tabEditor(new ToolsEditor(updateDriverContent),  path.toString(), driverName); 
                break;
             case 2 :
                tabEditor(new ToolsEditor(generateDriverContent),  path.toString(), driverName);
                break;
         }
     }
     
 }
 
     public void contextMenu() {
        projectWorkSpacePath = label.hierarchyTestON + "drivers/common"; 
        contextMenu = new ContextMenu();
        
        MenuItem openContextMenu = new MenuItem(label.contextOpen);
        MenuItem editContextMenu = new MenuItem("Edit As Config");
        
        openContextMenu.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent args0) {
                TreeItem<String> selectedTreeItem = driverExplorerTreeView.getSelectionModel().getSelectedItem();

            }
        });
         
        openContextMenu.setOnAction(new EventHandler<ActionEvent>() {

             @Override
             public void handle(ActionEvent t) {
                 
                 TreeItem<String> driverSelectedItem = driverExplorerTreeView.getSelectionModel().getSelectedItem();
                 
                    try {
                        String[] splitSelectedDriver = driverSelectedItem.getValue().split("\\.");

                        String path = null;
                        TreeItem selectedTreeItem = driverSelectedItem.getParent();
                        TreeItem selectedParentItem = selectedTreeItem.getParent();
                        
                        path = projectWorkSpacePath + "/" + driverSelectedItem.getParent().getParent().getValue() + "/" + driverSelectedItem.getParent().getValue()
                                + "/" + driverSelectedItem.getValue() + ".py";

                        if (driverSelectedItem.getParent().getValue().equals("emulator")) {
                            path = projectWorkSpacePath + "/" + driverSelectedItem.getParent().getParent().getValue() + "/" + driverSelectedItem.getParent().getValue()
                                    + "/" + driverSelectedItem.getValue() + ".py";
                        } else if (driverSelectedItem.getParent().getValue().equals("api")) {
                            path = projectWorkSpacePath + "/" + driverSelectedItem.getParent().getValue() + "/" + driverSelectedItem.getValue() + ".py";
                        } else if (driverSelectedItem.getParent().getValue().equals("tool")) {
                            path = projectWorkSpacePath + "/" + driverSelectedItem.getParent().getParent().getValue() + "/" + driverSelectedItem.getParent().getValue()
                                    + "/" + driverSelectedItem.getValue() + ".py";
                        } else if (driverSelectedItem.getParent().getValue().equals("cli")) {
                            path = projectWorkSpacePath + "/" + driverSelectedItem.getParent().getValue() + "/" + driverSelectedItem.getValue() + ".py";
                        }
                      
                        String fileContent = fileOperation.getContents(new File(path));
                     
                        tabEditor(new ToolsEditor(fileContent),  path, driverSelectedItem.getValue());


                    } catch (Exception e) {
                    }

             }
         });
        
        
        editContextMenu.setOnAction(new EventHandler<ActionEvent>() {

             @Override
             public void handle(ActionEvent t) {
                    TreeItem<String> driverSelectedItem = driverExplorerTreeView.getSelectionModel().getSelectedItem();
                    getConfig(driverSelectedItem.getValue());
             }
         });
        
        contextMenu.getItems().addAll(openContextMenu,editContextMenu);
        driverExplorerTreeView.contextMenuProperty().setValue(contextMenu);
        
    }
     
    public String getDriverPath(){
        TreeItem<String> driverSelectedItem = driverExplorerTreeView.getSelectionModel().getSelectedItem();
           String path = null;      
                    try {
                        String[] splitSelectedDriver = driverSelectedItem.getValue().split("\\.");

                        
                        TreeItem selectedTreeItem = driverSelectedItem.getParent();
                        TreeItem selectedParentItem = selectedTreeItem.getParent();
                        
                        path = projectWorkSpacePath + "/" + driverSelectedItem.getParent().getParent().getValue() + "/" + driverSelectedItem.getParent().getValue()
                                + "/" + driverSelectedItem.getValue() + ".py";

                        if (driverSelectedItem.getParent().getValue().equals("emulator")) {
                            path = projectWorkSpacePath + "/" + driverSelectedItem.getParent().getParent().getValue() + "/" + driverSelectedItem.getParent().getValue()
                                    + "/" + driverSelectedItem.getValue() + ".py";
                        } else if (driverSelectedItem.getParent().getValue().equals("api")) {
                            path = projectWorkSpacePath + "/" + driverSelectedItem.getParent().getValue() + "/" + driverSelectedItem.getValue() + ".py";
                        } else if (driverSelectedItem.getParent().getValue().equals("tool")) {
                            path = projectWorkSpacePath + "/" + driverSelectedItem.getParent().getParent().getValue() + "/" + driverSelectedItem.getParent().getValue()
                                    + "/" + driverSelectedItem.getValue() + ".py";
                        } else if (driverSelectedItem.getParent().getValue().equals("cli")) {
                            path = projectWorkSpacePath + "/" + driverSelectedItem.getParent().getValue() + "/" + driverSelectedItem.getValue() + ".py";
                        }
                        
                        
                    } catch (Exception e) {
                    }
        return path;
                    
                    
    } 
    
    public void openFile(String extension, String extension2) {
        File selected;
        String fileContent = "";
        open = new FileChooser();
        open.setInitialDirectory(new File(label.hierarchyTestON + "config/"));
        if ("".equals(extension2)) {
            open.getExtensionFilters().add(new FileChooser.ExtensionFilter("Display  only (*." + extension + ") files", "*." + extension));
        } else {
            open.getExtensionFilters().add(new FileChooser.ExtensionFilter("Display  only (*." + extension + ")" + "files", "*." + extension));
            open.getExtensionFilters().add(new FileChooser.ExtensionFilter("Display  only (*." + extension2 + ") files", "*." + extension2));
        }
        selected = open.showOpenDialog(contextMenu);
        try {
            fileContent = fileOperation.getContents(selected);
            
            String filename = selected.getName();
            
            tabEditor(new ToolsEditor(fileContent), selected.getAbsolutePath(), "");
        } catch (Exception e) {
        }

        editor.prefWidthProperty().bind(scene.widthProperty().subtract(200));
    }
    
}
