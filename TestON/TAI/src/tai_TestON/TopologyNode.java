
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

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.beans.property.DoubleProperty;
import javafx.beans.property.ObjectProperty;
import javafx.beans.property.SimpleObjectProperty;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Pos;
import javafx.geometry.Side;
import javafx.scene.Cursor;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.ContextMenu;
import javafx.scene.control.MenuItem;
import javafx.scene.control.MultipleSelectionModel;
import javafx.scene.control.SingleSelectionModel;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.control.TextField;
import javafx.scene.control.ToolBar;
import javafx.scene.control.Tooltip;
import javafx.scene.control.TreeItem;
import javafx.scene.control.TreeView;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.input.ClipboardContent;
import javafx.scene.input.DragEvent;
import javafx.scene.input.Dragboard;
import javafx.scene.input.MouseButton;
import javafx.scene.input.MouseDragEvent;
import javafx.scene.input.MouseEvent;
import javafx.scene.input.TransferMode;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Pane;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Line;
import javafx.scene.shape.Shape;
import javafx.scene.shape.StrokeLineCap;
import javafx.stage.Stage;

/**
 *
 * @author paxterra
 */
class TopologyNode {
    TAI_TestON OFAReference;

    public TopologyNode(TAI_TestON ref) {
        this.OFAReference = ref;
    }
    final ObservableList<Shape> shapes = FXCollections.observableArrayList();
    final ObservableList<Node> nodesPresent = FXCollections.observableArrayList();
    final ObservableList<ShapePair> intersections = FXCollections.observableArrayList();
    final ArrayList<Anchor2> anchorStore = new ArrayList<TopologyNode.Anchor2>();
    final ArrayList<String> insertedDeviceNameStore = new ArrayList<String>();
    final ArrayList<String> insertedDeviceLinkStore = new ArrayList<String>();
    final ArrayList<String> insertedDeviceNameCoordinates = new ArrayList<String>();
    Line line = new Line(33.0, 156.0, 43.0, 352.0);
    final HashMap<Node, String> insertedDeviceNameAndCoordinatesHash = new HashMap<Node, String>();
    ObjectProperty<BoundsType> selectedBoundsType = new SimpleObjectProperty<BoundsType>(BoundsType.LAYOUT_BOUNDS);
    final Tab canvasTab = new Tab("Canvas");
    boolean anchorFlag = false;
    boolean anchorFlagSwitch = false;
    TAILocale label = new TAILocale(new Locale("en", "EN"));
    Hashtable modifyHash = new Hashtable<>();
    
    enum BoundsType {

        LAYOUT_BOUNDS, BOUNDS_IN_LOCAL, BOUNDS_IN_PARENT
    }
    TreeView<String> driverExplorerTreeView;
    ArrayList<TextField> deviceNameList = new ArrayList<TextField>();
    TAITopology topoplogy;
    ArrayList<String> propertyValue = new ArrayList<String>();
    ArrayList<String> interFaceName = new ArrayList<String>();
    ArrayList<String> interFaceValue = new ArrayList<String>();
    // TreeView<String> driverExplorerTreeView ;
    ArrayList<String> webInfoList = new ArrayList<String>();
    ArrayList<String> webCisco = new ArrayList<String>();
    ArrayList<TreeMap<String, String>> arrayOfInterFaceHash;
    TreeMap<String, String> interFaceHashDetail = new TreeMap<String, String>();
    HashMap<String, String> webToplogyHash = new HashMap<String, String>();
    HashMap<String, String> linkTopologyHash = new HashMap<String, String>();
    ArrayList<HashMap<String, String>> arrayOfLinkTopologyHash = new ArrayList<HashMap<String, String>>();
    ArrayList<HashMap<String, String>> arrayOfwebTopologyHash;
    ArrayList<HashMap<String, String>> topodetails = new ArrayList<HashMap<String, String>>();
    String topoDeviceName;
    String topoDeviceType;
    ArrayList<String> topoEditorDeviceInfo = new ArrayList<String>();
    boolean switchCoordinateFlag = false;
    TAITopologyLink topologyLink = new TAITopologyLink();
    Line connecting = new Line();

    public VBox getNode(final String tplFilePath) {

        String tplPath = tplFilePath;
        VBox parentTopologyBox = new VBox();
        ToolBar canvasToolBar = new ToolBar();
        final Button lineButtonHorizontal = new Button();
        Tooltip horizontal = new Tooltip("Click to add link which connects devices in canvas");
        lineButtonHorizontal.setTooltip(horizontal);
        Image image = new Image(getClass().getResourceAsStream("/images/Link1.png"), 30.0, 30.0, true, true);
        ImageView imageNew = new ImageView(image);
        lineButtonHorizontal.setGraphic(imageNew);
        connecting.setId("Line");
        connecting.setStrokeLineCap(StrokeLineCap.ROUND);
        connecting.setStroke(Color.MIDNIGHTBLUE);
        connecting.setStrokeWidth(2.5);

        Button lineButtonVertical = new Button();
        Tooltip vertical = new Tooltip("Click to add vertical line in canvas");
        lineButtonVertical.setTooltip(vertical);

        // final Button deleteButton = new Button("Delete");

        final Button deleteAllButton = new Button();
        Tooltip delete = new Tooltip("Click to reset or clear canvas");
        deleteAllButton.setTooltip(delete);
        Image image2 = new Image(getClass().getResourceAsStream("/images/Refresh.png"));
        ImageView imageNew2 = new ImageView(image2);
        deleteAllButton.setGraphic(imageNew2);

        Image image1 = new Image(getClass().getResourceAsStream("/images/verticalLine.jpg"), 24.0, 24.0, true, true);
        ImageView imageNew1 = new ImageView(image1);
        lineButtonVertical.setGraphic(imageNew1);

        Button lineButtonSlantRight = new Button();
        Tooltip slantRight = new Tooltip("Click to add right slant line");
        lineButtonSlantRight.setTooltip(slantRight);
        Image image3 = new Image(getClass().getResourceAsStream("/images/SlantLineRight.jpg"), 24, 24, true, true);
        ImageView imageNew3 = new ImageView(image3);
        lineButtonSlantRight.setGraphic(imageNew3);

        Button lineButtonSlantLeft = new Button();
        Tooltip slantLeft = new Tooltip("Click to add right slant line");
        lineButtonSlantLeft.setTooltip(slantRight);
        Image image4 = new Image(getClass().getResourceAsStream("/images/SlantLineLeft.jpg"), 24, 24, true, true);
        ImageView imageNew4 = new ImageView(image4);
        lineButtonSlantLeft.setGraphic(imageNew4);

        // Button deleteButton = new Button();
        canvasToolBar.getItems().addAll(lineButtonHorizontal, deleteAllButton);
        HBox topologyBox = new HBox();
        TabPane topologyPane = new TabPane();
        topologyPane.setSide(Side.LEFT);
        final Tab topologyModifiedDriverExplorerTab = new Tab("DEVICES");
        topologyPane.setMaxWidth(250);

        
        String hostName =  label.hierarchyTestON + "/drivers/common";
        //try{hostName=InetAddress.ge;}catch(UnknownHostException x){}
        final Node rootIcon = new ImageView(new Image(getClass().getResourceAsStream("/images/project.jpeg"), 16, 16, true, true));
        TreeItem<String> driverExplorerTree = new TreeItem<String>("Drivers");
        // driverExplorerTree.setGraphic(rootIcon);
        File[] file = File.listRoots();

        
        Path name = new File(hostName).toPath();

        LoadDirectory treeNode = new LoadDirectory(name);

        treeNode.setExpanded(true);
        driverExplorerTree.getChildren().add(treeNode);
        // }
        //  driverExplorerTree.getChildren().add(treeNode);
        driverExplorerTree.setExpanded(true);

        //create the tree view
        driverExplorerTreeView = new TreeView<String>(driverExplorerTree);

        topologyModifiedDriverExplorerTab.setContent(driverExplorerTreeView);
        driverExplorerTreeView.setShowRoot(false);
        topologyPane.getTabs().add(topologyModifiedDriverExplorerTab);
        topologyModifiedDriverExplorerTab.setClosable(false);
        // topologyBox.getChildren().add(topologyPane);
        final TabPane topologyNewCanvas = new TabPane();
        //  topologyNewCanvas.setMaxWidth(700);
        topologyNewCanvas.setSide(Side.BOTTOM);
        // final Tab canvasTab = new Tab("Canvas");
        canvasTab.setClosable(false);

        //TextArea content = new TextArea();
        Button mew = new Button("CLICK");
        mew.setGraphic(rootIcon);
        HBox hBox1 = new HBox();
        hBox1.setPrefWidth(345);
        hBox1.setPrefHeight(200);
        hBox1.setStyle("-fx-border-color: blue;"
                + "-fx-border-width: 1;"
                + "-fx-border-style: solid;");
        //  insertImage(driverExplorerTree.getGraphic(),topologyModifiedDriverExplorerTab


        //  Group content = new Group();
        // content.getChildren().add(new TextArea());
        // content.sceneToLocal(123)
        Pane box1 = new Pane();
        box1.setPrefWidth(900);//500
        box1.setPrefHeight(500);//200
        canvasTab.setContent(box1);
       
        topologyNewCanvas.getTabs().add(canvasTab);

        //   DraggableNode node = new DraggableNode();


        
        lineButtonHorizontal.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent arg0) {
                //throw new UnsupportedOperationException("Not supported yet.");
                final Line connecting = new Line(33, 43, 33, 43);
                connecting.setId("Line");
                connecting.setStrokeLineCap(StrokeLineCap.ROUND);
                connecting.setStroke(Color.MIDNIGHTBLUE);
                connecting.setStrokeWidth(2.5);

                final TopologyNode.Anchor anchor1 = new TopologyNode.Anchor("Anchor 1", connecting.startXProperty(), connecting.startYProperty());
                final TopologyNode.Anchor anchor2 = new TopologyNode.Anchor("Anchor 2", connecting.endXProperty(), connecting.endYProperty());
                //anchor1.setVisible(false);
                //anchor2.setVisible(false);
                anchor1.setFill(Color.TRANSPARENT.deriveColor(1, 1, 1, 0.5));
                anchor2.setFill(Color.TRANSPARENT.deriveColor(1, 1, 1, 0.5));
                //          final Line connecting = new Line();
                //        connecting.setStrokeWidth(3);
                //connecting.setEndX(90);
                //  connecting.setLayoutX(33);
                //   connecting.setLayoutY(33);

                Circle[] circles = {anchor1, anchor2};
                for (Circle circle : circles) {
                    enableDrag(circle);
                }

                enableDragLineWithAnchors(connecting, anchor1, anchor2);
                anchor1.setOnMouseEntered(new EventHandler<MouseEvent>() {

                    @Override
                    public void handle(MouseEvent arg0) {
                        //throw new UnsupportedOperationException("Not supported yet.");
                        anchor1.setFill(Color.GOLD.deriveColor(1, 1, 1, 0.5));
                        anchor1.setVisible(true);
                        anchor2.setVisible(true);
                    }
                });

                anchor1.setOnMouseExited(new EventHandler<MouseEvent>() {

                    @Override
                    public void handle(MouseEvent arg0) {
                        //throw new UnsupportedOperationException("Not supported yet.");
                        anchor1.setFill(Color.TRANSPARENT.deriveColor(1, 1, 1, 0.5));
                        anchor1.setVisible(false);
                        anchor2.setVisible(false);
                    }
                });

                anchor2.setOnMouseEntered(new EventHandler<MouseEvent>() {

                    @Override
                    public void handle(MouseEvent arg0) {
                        //throw new UnsupportedOperationException("Not supported yet.");
                        anchor2.setFill(Color.GOLD.deriveColor(1, 1, 1, 0.5));
                        anchor1.setVisible(true);
                        anchor2.setVisible(true);
                    }
                });
                anchor2.setOnMouseExited(new EventHandler<MouseEvent>() {

                    @Override
                    public void handle(MouseEvent arg0) {
                        //throw new UnsupportedOperationException("Not supported yet.");
                        anchor2.setFill(Color.TRANSPARENT.deriveColor(1, 1, 1, 0.5));
                        anchor1.setVisible(false);
                        anchor2.setVisible(false);
                    }
                });

                connecting.setOnMouseEntered(new EventHandler<MouseEvent>() {

                    @Override
                    public void handle(MouseEvent arg0) {
                        // throw new UnsupportedOperationException("Not supported yet.");

                        //connecting.setFill(Color.GOLD.brighter());
                        connecting.setStroke(Color.GOLD);
                        anchor1.setVisible(true);
                        anchor2.setVisible(true);
                        // connecting.setStyle("-fx-border: darkgreen");

                    }
                });
                connecting.setOnMouseExited(new EventHandler<MouseEvent>() {

                    @Override
                    public void handle(MouseEvent arg0) {
                        //throw new UnsupportedOperationException("Not supported yet.");
                        connecting.setStroke(Color.MIDNIGHTBLUE);
                        anchor1.setVisible(false);
                        anchor2.setVisible(false);

                    }
                });
                // connecting.se
                final DraggableNode contentLine = new DraggableNode();

                connecting.setOnMouseClicked(new EventHandler<MouseEvent>() {

                    @Override
                    public void handle(MouseEvent arg0) {
                        if (arg0.getClickCount() == 2) {

                            topologyLink.start(new Stage());

                            if (!arrayOfLinkTopologyHash.isEmpty()) {
                                for (HashMap<String, String> linkHash : arrayOfLinkTopologyHash) {
                                    Set linkSet = linkHash.entrySet();
                                    Iterator linkHashDetailIterator = linkSet.iterator();
                                    while (linkHashDetailIterator.hasNext()) {

                                        Map.Entry linkMap = (Map.Entry) linkHashDetailIterator.next();
                                       

                                        if (linkMap.getKey().toString().equals(connecting.getId())) {
                                            String[] linkValues = linkMap.getValue().toString().split("_");
                                            


                                            topologyLink.nameText.setText(linkValues[0]);
                                            topologyLink.typeText.setText(linkValues[1]);
                                            topologyLink.devicesInTopoEditor.setEditable(true);
                                            topologyLink.devicesInTopoEditor.getSelectionModel().select(linkValues[2]);
                                            topologyLink.interfaceList2.setEditable(true);
                                            topologyLink.interfaceList2.getSelectionModel().select(linkValues[3]);
                                            topologyLink.destDevicesInTopoEditor.setEditable(true);
                                            topologyLink.destDevicesInTopoEditor.getSelectionModel().select(linkValues[4]);
                                            topologyLink.interfaceList4.setEditable(true);
                                            topologyLink.interfaceList4.getSelectionModel().select(linkValues[5]);


                                            //}
                                        }



                                    }

                                }
                            }

                        
                            for (String string : topoEditorDeviceInfo) {
                                topologyLink.devicesInTopoEditor.getItems().add(string);
                                topologyLink.destDevicesInTopoEditor.getItems().add(string);
                            }

                    
                            topologyLink.devicesInTopoEditor.setOnAction(new EventHandler<ActionEvent>() {

                                @Override
                                public void handle(ActionEvent arg0) {
                                   
                                    try {
                                        
                                        for (TreeMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
                                            Set set = interFaceDetail.entrySet();
                                            Iterator interFaceHashDetailIterator = set.iterator();
                                            while (interFaceHashDetailIterator.hasNext()) {
                                                Map.Entry me = (Map.Entry) interFaceHashDetailIterator.next();

                                                String[] deviceNameAndiniterFaceValue = me.getValue().toString().split("\\_");


                                                if (deviceNameAndiniterFaceValue[1].equals(topologyLink.devicesInTopoEditor.getSelectionModel().getSelectedItem())) {
                                                    if (!me.getKey().toString().equals("")) {
                                                        topologyLink.interfaceList2.getItems().add(me.getKey().toString());

                                                    }
                                                }

                                            }
                                        }
                                    } catch (Exception e) {
                                    }


                                }
                            });

                            topologyLink.destDevicesInTopoEditor.setOnAction(new EventHandler<ActionEvent>() {

                                @Override
                                public void handle(ActionEvent arg0) {

                                    topologyLink.interfaceList4.getItems().clear();
                                    try {
                                     
                                        for (TreeMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
                                            Set set = interFaceDetail.entrySet();
                                            Iterator interFaceHashDetailIterator = set.iterator();
                                            while (interFaceHashDetailIterator.hasNext()) {
                                                Map.Entry me = (Map.Entry) interFaceHashDetailIterator.next();


                                                String[] deviceNameAndiniterFaceValue = me.getValue().toString().split("\\_");



                                                
                                                if (deviceNameAndiniterFaceValue[1].equals(topologyLink.destDevicesInTopoEditor.getSelectionModel().getSelectedItem())) {
                                                   
                                                    if (!me.getKey().toString().equals("")) {
                                                     
                                                        topologyLink.interfaceList4.getItems().add(me.getKey().toString());
                                                    }
                                                }

                                            }
                                        }
                                    } catch (Exception e) {
                                    }
                                }
                            });
                            topologyLink.cancelButton.setOnAction(new EventHandler<ActionEvent>() {

                                @Override
                                public void handle(ActionEvent arg0) {
                                    topologyLink.copyStage.close();
                                }
                            });
                            topologyLink.finishSelectedLink.setOnAction(new EventHandler<ActionEvent>() {

                                @Override
                                public void handle(ActionEvent arg0) {
                        
                                    connecting.setId(topologyLink.nameText.getText() + "_" + connecting.getStartX() + "_" + connecting.getStartY() + "_" + connecting.getEndX() + "_" + connecting.getEndY());
                                    String detailedString = topologyLink.nameText.getText() + "_" + topologyLink.typeText.getText() + "_" + topologyLink.devicesInTopoEditor.getSelectionModel().getSelectedItem() + "_" + topologyLink.interfaceList2.getSelectionModel().getSelectedItem() + "_" + topologyLink.destDevicesInTopoEditor.getSelectionModel().getSelectedItem() + "_" + topologyLink.interfaceList4.getSelectionModel().getSelectedItem() + "_";
                                    linkTopologyHash.put(connecting.getId(), detailedString);
                                    arrayOfLinkTopologyHash.add(linkTopologyHash);
                                    topologyLink.copyStage.close();
                                }
                            });


                        } else if (arg0.getButton() == MouseButton.SECONDARY) {

                            deleteLineContextMenu(contentLine, connecting, arg0);

                        }

                    }
                });

                
                Pane created = (Pane) canvasTab.getContent();

                created.getChildren().addAll(connecting, anchor1, anchor2);
            }
        });

        lineButtonSlantRight.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent arg0) {
                final Line connecting = new Line();
                connecting.setStrokeWidth(3);
                connecting.setEndX(90);
                connecting.setRotate(135);
                connecting.setLayoutX(33);
                connecting.setLayoutY(33);
                final DraggableNode contentLine = new DraggableNode();
                contentLine.getChildren().add(connecting);

                Pane created = (Pane) canvasTab.getContent();
                contentLine.setOnMouseClicked(new EventHandler<MouseEvent>() {

                    @Override
                    public void handle(MouseEvent arg0) {
                        if (arg0.getClickCount() == 2) {
                            TAITopologyLink topologyLink = new TAITopologyLink();
                            topologyLink.start(new Stage());
                        } else if (arg0.getButton() == MouseButton.SECONDARY) {

                            deleteLineContextMenu(contentLine, connecting, arg0);

                        }

                    }
                });
                created.getChildren().addAll(contentLine);
            }
        });

        lineButtonSlantLeft.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent arg0) {
                //throw new UnsupportedOperationException("Not supported yet.");
                final Line connecting = new Line();
                connecting.setStrokeWidth(3);
                connecting.setEndX(90);
                connecting.setRotate(45);
                // connecting.se
                connecting.setLayoutX(33);
                connecting.setLayoutY(33);
                final DraggableNode contentLine = new DraggableNode();
                contentLine.getChildren().add(connecting);

                Pane created = (Pane) canvasTab.getContent();
                contentLine.setOnMouseClicked(new EventHandler<MouseEvent>() {

                    @Override
                    public void handle(MouseEvent arg0) {
                        if (arg0.getClickCount() == 2) {
                            TAITopologyLink topologyLink = new TAITopologyLink();
                            topologyLink.start(new Stage());
                        } else if (arg0.getButton() == MouseButton.SECONDARY) {

                            deleteLineContextMenu(contentLine, connecting, arg0);

                        }


                    }
                });

                //  created.setLayoutY(400);
                created.getChildren().addAll(contentLine);
            }
        });

        deleteAllButton.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent arg0) {
                //throw new UnsupportedOperationException("Not supported yet.");
                Pane pane = (Pane) canvasTab.getContent();
                ObservableList<Node> list = pane.getChildren();
                pane.getChildren().removeAll(list);

            }
        });


        lineButtonVertical.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent arg0) {
                //throw new UnsupportedOperationException("Not supported yet.");
                final Line connecting = new Line();
                connecting.setStrokeWidth(3);
                connecting.setEndY(90);
                connecting.setLayoutX(33);
                connecting.setLayoutY(33);
                // connecting.se
                final DraggableNode contentLine = new DraggableNode();
                contentLine.setOnMouseClicked(new EventHandler<MouseEvent>() {

                    @Override
                    public void handle(MouseEvent arg0) {
                        if (arg0.getClickCount() == 2) {
                            TAITopologyLink topologyLink = new TAITopologyLink();
                            topologyLink.start(new Stage());
                        } else if (arg0.getButton() == MouseButton.SECONDARY) {

                            deleteLineContextMenu(contentLine, connecting, arg0);

                        }
                    }
                });

                contentLine.getChildren().add(connecting);

                Pane created = (Pane) canvasTab.getContent();

                created.getChildren().addAll(contentLine);
            }
        });



        driverExplorerTreeView.setOnDragDetected(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
                // throw new UnsupportedOperationException("Not supported yet.");
                final MultipleSelectionModel<TreeItem<String>> selectedItem = driverExplorerTreeView.getSelectionModel();
               
                try {

                    Image i = new Image(getClass().getResourceAsStream(selectedItem.getSelectedItem().getGraphic().getId()), 60, 60, true, true);
                    Dragboard db = driverExplorerTreeView.startDragAndDrop(TransferMode.COPY);


                    ClipboardContent content = new ClipboardContent();

                    content.putImage(i);
                    db.setContent(content);

                    arg0.consume();


                  
                } catch (Exception e) {
                }

                // }
                // }
                // });

            }
        });
        final Pane pane = (Pane) canvasTab.getContent();
        pane.setOnDragOver(new EventHandler<DragEvent>() {

            @Override
            public void handle(DragEvent t) {
                //   throw new UnsupportedOperationException("Not supported yet.");

                Dragboard db = t.getDragboard();

                if (db.hasImage()) {
                    t.acceptTransferModes(TransferMode.COPY);
                }

                t.consume();


            }
        });

        pane.setOnDragDropped(new EventHandler<DragEvent>() {

            @Override
            public void handle(DragEvent event) {

                Dragboard db = event.getDragboard();

                if (db.hasImage()) {
                 
                    insertImage(db.getImage(), pane, tplFilePath, event.getX(), event.getY());

                    //insertImage(db.getImage(), tplFilePath,pane,event.getX(),event.getY());

                    event.setDropCompleted(true);
                } else {
                    event.setDropCompleted(false);
                }

                event.consume();
            }
        });
        SingleSelectionModel<Tab> tab = topologyNewCanvas.getSelectionModel();
        tab.getSelectedItem().getContent().setOnMouseClicked(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
                //throw new UnsupportedOperationException("Not supported yet.");

                SingleSelectionModel<Tab> tab1 = topologyNewCanvas.getSelectionModel();
               

            }
        });




        ObservableList<TreeItem<String>> rest1 = treeNode.getChildren();



        Iterator<TreeItem<String>> eachTreeItem1 = rest1.iterator();
        while (eachTreeItem1.hasNext()) {
            TreeItem<String> treeItem = eachTreeItem1.next();
            ObservableList<TreeItem<String>> restChildren = treeItem.getChildren();

            Iterator<TreeItem<String>> eachTreeItem2 = restChildren.iterator();
            while (eachTreeItem2.hasNext()) {
                TreeItem<String> treeItem1 = eachTreeItem2.next();
                ObservableList<TreeItem<String>> childrenLastLevel = treeItem1.getChildren();
                
                Iterator<TreeItem<String>> eachTreeItem3 = childrenLastLevel.iterator();
                while(eachTreeItem3.hasNext()){
                    TreeItem<String> treeItem2 = eachTreeItem3.next();
                    
                 ///****************************************************************************   
                    
                    TAIParamDeviceName tplObject = new TAIParamDeviceName(tplFilePath, "");
                tplObject.parseParamFile();


             
                for (String namehere : tplObject.getParamDeviceName()) {


                  
                    for (String deviceName : tplObject.getParamDeviceType()) {
                      
                        if (deviceName.equals(tplObject.getdeviceNameAndType().get(namehere))) {
                            try {
                                String typeDevice = treeItem2.getValue().replaceAll("\\s+", "");
                                String parent = treeItem2.getParent().getValue().replaceAll("\\s+", "");
                                
                                String deviceNameWithout = deviceName.toString().replaceAll("\\s+", "");

                             
                                
                                if (typeDevice.equals(deviceNameWithout)) {

                                    String coordinates = tplObject.getdeviceNameAndCoordinate().get(namehere);
                                 
                                    try {
                       
                                        
                                        Image i = new Image(treeItem2.getGraphic().getId(), 60, 60, true, true);
                                        String coordinate = tplObject.getCoordinateName().toString();
                                        
                                        
                                        
                                        
                                        if (!insertedDeviceNameStore.contains(namehere)) {
                                          
                                            if (!insertedDeviceNameCoordinates.contains(coordinates)) {
                                                
                                                
                                                insertImage2(i, (Pane) canvasTab.getContent(), namehere, coordinates, parent, typeDevice, tplFilePath);

                                                insertedDeviceNameStore.add(namehere);
                                                insertedDeviceNameCoordinates.add(coordinates);
                                            } else {
                                                
                                                if (!insertedDeviceLinkStore.contains(namehere)) {

                                                    //    insertLine(tplFilePath, (Pane) canvasTab.getContent(), namehere);
                                                    insertedDeviceLinkStore.add(namehere);
                                                }
                                            }

                                        }
                                    } catch (Exception e) {
                                    }

                                } else {
                                }
                            } catch (Exception e) {
                            }

                        }
                        
                    }


                }
                    
                    
                    
                    
                    
                    
                    
                    
                 //********************************************************************************   
                }

            }
        }
        for (String nam : insertedDeviceLinkStore) {
          
            insertLine(tplFilePath, (Pane) canvasTab.getContent(), nam);
        }

        topologyBox.getChildren().addAll(topologyPane, topologyNewCanvas);
        parentTopologyBox.getChildren().addAll(canvasToolBar, topologyBox);
        return parentTopologyBox;
    }
    
    
   
   public void insertImage(Image i, Pane hb, final String tplFilePath, Double x, Double y) {
      
        //anchorFlag = false;
        final TextField text = new TextField();
        final String[] deviceInfo;
        final String topologyFileDemo;
        
        final Button closeButton = new Button();
        Tooltip close = new Tooltip();
        close.setText("Delete this device");
        closeButton.setTooltip(close);
        Image image = new Image(getClass().getResourceAsStream("/images/close_icon2.jpg"), 12, 12, true, true);
        ImageView imageNew3 = new ImageView(image);
        closeButton.setGraphic(imageNew3);
        closeButton.setStyle("-fx-background-color: white;");

        text.setId(driverExplorerTreeView.getSelectionModel().getSelectedItem().getValue().toString() + "_" + driverExplorerTreeView.getSelectionModel().getSelectedItem().getParent().getValue());
        deviceInfo = text.getId().split("\\_");
      
        deviceNameList.add(text);
        text.setPrefWidth(100);
        ImageView iv = new ImageView();
        iv.setImage(i);

        
       
        final DraggableNode content = new DraggableNode();
        final VBox hbox = new VBox();
        hbox.setPrefWidth(80);
        hbox.setPrefHeight(100);


        hbox.setOnMouseEntered(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
                //throw new UnsupportedOperationException("Not supported yet.");
                if (content.getId() != null) {

                    hbox.setStyle("-fx-border-color: Gold");

                    // final Line connecting = new Line(33, 43, 33, 43);
                    String[] splitforCoordinates = content.getId().split(",");

                    Double x = new Double(splitforCoordinates[0]);
                    Double y = new Double(splitforCoordinates[1]);
                    connecting.setLayoutX(x + 70);
                    connecting.setLayoutY(y + 60);


                } //else {
                // }
            }
        });

        hbox.setOnMouseExited(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
                hbox.setStyle("-fx-border-color: Transparent");
                Double xcoordinate = content.getLayoutX();
                Double ycoordinate = content.getLayoutY();
                TAITopology device = new TAITopology();
                content.setId(xcoordinate.toString() + "," + ycoordinate.toString());
                
            }
        });



        hbox.setOnMouseClicked(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {

                if (anchorFlag == false) {
                    if (arg0.getClickCount() == 1) {

                        final Line con = new Line();
                        // connecting.setId("Line");
                        con.setStrokeLineCap(StrokeLineCap.ROUND);
                        con.setStroke(Color.MIDNIGHTBLUE);
                        con.setStrokeWidth(2.0);

                        final Line con1 = new Line();
                        con1.setStrokeLineCap(StrokeLineCap.ROUND);
                        con1.setStroke(Color.MIDNIGHTBLUE);
                        con1.setStrokeWidth(2.0);
                        final Line con2 = new Line();
                        con2.setStrokeLineCap(StrokeLineCap.ROUND);
                        con2.setStroke(Color.MIDNIGHTBLUE);
                        con2.setStrokeWidth(2.0);

                        final Line con3 = new Line();
                        con3.setStrokeLineCap(StrokeLineCap.ROUND);
                        con3.setStroke(Color.MIDNIGHTBLUE);
                        con3.setStrokeWidth(2.0);


                     



                        final Anchor anchor3 = new Anchor("anchor3", con.startXProperty(), con.startYProperty());
                        final Anchor anchor4 = new Anchor("anchor4", con.endXProperty(), con.endYProperty());

                        final Anchor anchor5 = new Anchor("anchor5", con1.startXProperty(), con1.startYProperty());
                        final Anchor anchor6 = new Anchor("anchor6", con1.endXProperty(), con1.endYProperty());

                        final Anchor anchor7 = new Anchor("anchor7", con2.startXProperty(), con2.startYProperty());
                        final Anchor anchor8 = new Anchor("anchor8", con2.endXProperty(), con2.endYProperty());

                        final Anchor anchor9 = new Anchor("anchor9", con3.startXProperty(), con3.startYProperty());
                        final Anchor anchor10 = new Anchor("anchor10", con3.endXProperty(), con3.endYProperty());

                        final Pane hb = (Pane) canvasTab.getContent();
                      
                        anchor3.setLayoutX(content.getLayoutX());
                        anchor3.setLayoutY(content.getLayoutY());
                        anchor3.setVisible(false);
                        anchor4.setLayoutX(content.getLayoutX() + 40);
                        anchor4.setLayoutY(content.getLayoutY());

                        anchor5.setLayoutX(content.getLayoutX());
                        anchor5.setLayoutY(content.getLayoutY());
                        anchor5.setVisible(false);
                        anchor6.setLayoutX(content.getLayoutX() + 40);
                        anchor6.setLayoutY(content.getLayoutY() + 100);

                        anchor7.setLayoutX(content.getLayoutX());
                        anchor7.setLayoutY(content.getLayoutY());
                        anchor7.setVisible(false);
                        anchor8.setLayoutX(content.getLayoutX());
                        anchor8.setLayoutY(content.getLayoutY() + 50);


                        anchor9.setLayoutX(content.getLayoutX());
                        anchor9.setLayoutY(content.getLayoutY());
                        anchor9.setVisible(false);
                        anchor10.setLayoutX(content.getLayoutX() + 80);
                        anchor10.setLayoutY(content.getLayoutY() + 50);

                        con1.setLayoutX(anchor6.getLayoutX());
                        con1.setLayoutY(anchor6.getLayoutY());
                        con.setLayoutX(anchor4.getLayoutX());
                        con.setLayoutY(anchor4.getLayoutY());
                        con2.setLayoutX(anchor8.getLayoutX());
                        con2.setLayoutY(anchor8.getLayoutY());
                        con3.setLayoutX(anchor10.getLayoutX());
                        con3.setLayoutY(anchor10.getLayoutY());


                        con.setId("connectingLine");

                        con.setLayoutX(anchor4.getLayoutX());
                        con.setLayoutY(anchor4.getLayoutY());



                        anchorFlag = true;
                        hb.getChildren().addAll(con, anchor3, anchor4, con1, anchor5, anchor6, con2, anchor7, anchor8, con3, anchor9, anchor10);
                        
                        
           final ArrayList<Node> removeNodes = new ArrayList();             
               closeButton.setOnAction(new EventHandler<ActionEvent>() {

                            @Override
                            public void handle(ActionEvent t) {
                                
                                                Node parent = hbox.getParent();
                            ObservableList<Node> allCurrentNode = hb.getChildren();



                for (Node node : allCurrentNode) {
                    if (node.toString().contains("Line")) {
                        if (!node.toString().matches("Line[id=Line[id=null,null]]")) {
                         
                            if (node.getId() != null) {
                                String[] startLineNode = node.getId().split(",");

                                Integer nodeHash = content.hashCode();
                                if (nodeHash.toString().equals(startLineNode[0])) {
                               

                                    removeNodes.add(node);


                                }
                                if (startLineNode.length == 2) {
                                    if (nodeHash.toString().equals(startLineNode[1])) {

                                        removeNodes.add(node);

                                    }
                                }
                            }

                        }


                       
                    }
                }

                for (Node removenode : removeNodes) {
                    hb.getChildren().remove(removenode);
                                   
                }
                hb.getChildren().remove(content);
                                
                                  anchorFlag = false;
                                  hb.getChildren().removeAll(con, anchor3, anchor4, con1, anchor5, anchor6, con2, anchor7, anchor8, con3, anchor9, anchor10);
                            }
                        });
                        final ObservableList<Node> allNodeInCanvas = hb.getChildren();

  HashMap<Node,String> anchorNodeHash = new HashMap();
  anchorNodeHash.put(anchor4,anchor4.getId());
  anchorNodeHash.put(anchor6, anchor6.getId());
  anchorNodeHash.put(anchor8, anchor8.getId());
  anchorNodeHash.put(anchor10, anchor10.getId());
  anchorNodeHash.put(con1, con1.getId());
  anchorNodeHash.put(con2, con2.getId());
  anchorNodeHash.put(con3, con3.getId());
  anchorNodeHash.put(con, con.getId());


                        anchorsInsideImageNode(anchor4, 40, 50, hb, content, hbox, con,anchorNodeHash);

                        anchorsInsideImageNode(anchor6, 40, 50, hb, content, hbox, con1,anchorNodeHash);

                        anchorsInsideImageNode(anchor8, 40, 50, hb, content, hbox, con2,anchorNodeHash);

                        anchorsInsideImageNode(anchor10, 40, 50, hb, content, hbox, con3,anchorNodeHash);


                        hbox.setOnMouseDragged(new EventHandler<MouseEvent>() {

                            @Override
                            public void handle(MouseEvent t) {
                                anchorFlag = false;
                                hb.getChildren().removeAll(anchor3, anchor4, anchor5, anchor6, anchor7, anchor8, anchor9, anchor10, con, con1, con2, con3);
                            }
                        });
                        
                        

                        hbox.setOnMouseMoved(new EventHandler<MouseEvent>() {

                            @Override
                            public void handle(MouseEvent arg0) {
                                boolean exitFlag = false;
                                for (int i = 0; i <= 80; i++) {
                                    for (int j = 0; j <= 100; j++) {
                                        Double x1 = content.getLayoutX() + 482.0;
                                        Double y1 = content.getLayoutY() + 142.0;
                                        Double x11 = x1 + i;
                                        Double y11 = y1 + j;
                                        if (x11 == arg0.getSceneX()) {
                                            if (y11 == arg0.getSceneY()) {
                                                exitFlag = true;

                                            }
                                        }
                                    }
                                }
                                if (exitFlag == false) {
                                    hbox.setStyle("-fx-border-color: Transparent");
                                    anchorFlag = false;
                                    hb.getChildren().removeAll(con, con1, con2, con3, anchor4, anchor5, anchor6, anchor7, anchor8, anchor9, anchor10);
                                }


                            }
                        });




                        hbox.setOnMouseExited(new EventHandler<MouseEvent>() {

                            @Override
                            public void handle(MouseEvent arg0) {
                                boolean exitFlag = false;
                                for (int i = 0; i <= 80; i++) {
                                    for (int j = 0; j <= 100; j++) {
                                        Double x1 = content.getLayoutX() + 482.0;
                                        Double y1 = content.getLayoutY() + 142.0;
                                        Double x11 = x1 + i;
                                        Double y11 = y1 + j;
                                        if (x11 == arg0.getSceneX()) {
                                            if (y11 == arg0.getSceneY()) {
                                                exitFlag = true;

                                            }
                                            
                                        }
                                      
                                    }
                                }
                                if (exitFlag == false) {
                                    hbox.setStyle("-fx-border-color: Transparent");
                                    anchor4.setVisible(false);
                                    con.setVisible(false);
                                    anchor6.setVisible(false);
                                    con1.setVisible(false);
                                    anchor8.setVisible(false);
                                    con2.setVisible(false);
                                    anchor10.setVisible(false);
                                    con3.setVisible(false);
                                    anchorFlag = false;
                                    hb.getChildren().removeAll(anchor3, anchor4, anchor5, anchor6, anchor7, anchor8, anchor9, anchor10, con, con1, con2, con3);
                                }
                            }
                        });

                      


                    }
                }
                if (arg0.getClickCount() == 2) {
                 
                    if (deviceInfo[0].equals("fvtapidriver") || deviceInfo[0].equals("poxclidriver") || deviceInfo[0].equals("mininetclidriver") || deviceInfo[0].equals("dpctlclidriver")
                                || deviceInfo[0].equals("floodlightclidriver") || deviceInfo[0].equals("flowvisorclidriver") || deviceInfo[0].equals("hpswitchdriver")
                                || deviceInfo[0].equals("remotevmdriver") || deviceInfo[0].equals("remotepoxdriver") || deviceInfo[0].equals("flowvisordriver") || deviceInfo[0].equals("switchclidriver")) {

                        try {
                            topoplogy = new TAITopology();
                            topoplogy.start(new Stage());
                        } catch (Exception ex) {
                            Logger.getLogger(TopologyWizard.class.getName()).log(Level.SEVERE, null, ex);
                        }

                        topoplogy.cancelButton.setOnAction(new EventHandler<ActionEvent>() {

                            @Override
                            public void handle(ActionEvent arg0) {
                                topoplogy.copyStage.close();
                            }
                        });
                        topoplogy.save.setOnAction(new EventHandler<ActionEvent>() {

                            @Override
                            public void handle(ActionEvent arg0) {

                                topoplogy.getHostName = topoplogy.hostNameText.getText();
                                topoplogy.getUserName = topoplogy.userNameText.getText();
                                topoplogy.getPassword = topoplogy.passwordText.getText();



                                for (int i = 0; i < topoplogy.deviceTable.getItems().size(); i++) {
                                    topoplogy.deviceTable.getSelectionModel().select(i);
                                    interFaceHashDetail.put(topoplogy.deviceTable.getSelectionModel().getSelectedItem().getDeviceName().getText(), topoplogy.deviceTable.getSelectionModel().getSelectedItem().getDeviceType().getText() + "_" + text.getText());
                                    arrayOfInterFaceHash = new ArrayList();
                                    arrayOfInterFaceHash.add(interFaceHashDetail);
                                }

                               
                                propertyValue.add(text.getText() + "\n" + topoplogy.getHostName + "\n" + topoplogy.getUserName + "\n" + topoplogy.getPassword + "\n" + topoplogy.getTranportProtocol + "\n" + deviceInfo[0] + "\n" + topoplogy.getPort + "\n" + content.getId());
                                topoplogy.copyStage.close();
                            }
                        });
                    }
                    if (deviceInfo[1].equals("fvtapidriver") || deviceInfo[1].equals("poxclidriver") || deviceInfo[1].equals("mininetclidriver") || deviceInfo[1].equals("dpctlclidriver")
                                || deviceInfo[1].equals("floodlightclidriver") || deviceInfo[1].equals("flowvisorclidriver") || deviceInfo[1].equals("hpswitchdriver")
                                || deviceInfo[1].equals("remotevmdriver") || deviceInfo[1].equals("remotepoxdriver") || deviceInfo[1].equals("flowvisordriver") || deviceInfo[1].equals("switchclidriver")) {

                        try {
                            topoplogy = new TAITopology();
                            topoplogy.start(new Stage());
                        } catch (Exception ex) {
                            Logger.getLogger(TopologyWizard.class.getName()).log(Level.SEVERE, null, ex);
                        }

                        topoplogy.cancelButton.setOnAction(new EventHandler<ActionEvent>() {

                            @Override
                            public void handle(ActionEvent arg0) {
                                topoplogy.copyStage.close();
                            }
                        });
                        try {
                            topoplogy.save.setOnAction(new EventHandler<ActionEvent>() {

                                @Override
                                public void handle(ActionEvent arg0) {

                                    topoplogy.getHostName = topoplogy.hostNameText.getText();
                                    topoplogy.getUserName = topoplogy.userNameText.getText();
                                    topoplogy.getPassword = topoplogy.passwordText.getText();
                                    topoplogy.getTranportProtocol = topoplogy.transportList.getSelectionModel().getSelectedItem().toString();
                                    topoplogy.getPort = topoplogy.portText.getText();



                                    for (int i = 0; i < topoplogy.deviceTable.getItems().size(); i++) {
                                        topoplogy.deviceTable.getSelectionModel().select(i);
                                        interFaceHashDetail.put(topoplogy.deviceTable.getSelectionModel().getSelectedItem().getDeviceName().getText(), topoplogy.deviceTable.getSelectionModel().getSelectedItem().getDeviceType().getText() + "_" + text.getText());
                                        arrayOfInterFaceHash = new ArrayList();
                                        arrayOfInterFaceHash.add(interFaceHashDetail);
                                    }

                                   
                                    propertyValue.add(text.getText() + "\n" + topoplogy.getHostName + "\n" + topoplogy.getUserName + "\n" + topoplogy.getPassword + "\n" + topoplogy.getTranportProtocol + "\n" + deviceInfo[0] + "\n" + topoplogy.getPort + "\n" + content.getId());
                                    topoplogy.copyStage.close();
                                }
                            });

                        } catch (Exception e) {
                        }


                    } 

                }
            }
        });
       
        
        content.setOnMouseExited(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
                //throw new UnsupportedOperationException("Not supported yet.");
                Double xcoordinate = content.getLayoutX();
                Double ycoordinate = content.getLayoutY();
                TAITopology device = new TAITopology();
                content.setId(xcoordinate.toString() + "," + ycoordinate.toString());

            }
        });
        
        closeActionForAnchorsRemoval(closeButton, hbox, null, content);
        hbox.getChildren().addAll(closeButton, iv, text);
        hbox.setId(iv.toString());
        text.setPromptText("Device Name");
        content.getChildren().add(hbox);
        content.setLayoutX(x - 40);
        content.setLayoutY(y - 30);
        hb.getChildren().add(content);
    }

   public void insertImage2(Image i, final Pane hb, final String txt, String coordinates, final String deviceParent, final String deviceName, final String tplFilePath) {
      
        final TextField text = new TextField(txt);
        final String[] deviceInfo;
        
         final Button closeButton = new Button();
        Tooltip close = new Tooltip();
        close.setText("Delete this device");
        closeButton.setTooltip(close);
        Image image = new Image(getClass().getResourceAsStream("/images/close_icon2.jpg"), 12, 12, true, true);
        ImageView imageNew3 = new ImageView(image);
        closeButton.setGraphic(imageNew3);
        closeButton.setStyle("-fx-background-color: white;");
        topoEditorDeviceInfo.add(txt);
        String[] coordinatesSplit = coordinates.split(",");
        Double x = Double.valueOf(coordinatesSplit[0]);
        Double y = Double.valueOf(coordinatesSplit[1]);
        deviceNameList.add(text);
        text.setPrefWidth(100);
        final ImageView iv = new ImageView();
        iv.setImage(i);
        final DraggableNode content = new DraggableNode();
        final VBox hbox = new VBox();
        hbox.setPrefWidth(80);
        hbox.setPrefHeight(100);
        final HBox hor = new HBox();
        hor.setAlignment(Pos.CENTER);
        hor.setPrefWidth(100);
        hor.setPrefHeight(80);

        final TAIParamDeviceName tplObject = new TAIParamDeviceName(tplFilePath, "");
        tplObject.parseParamFile();
        final Line connecting = new Line();
        connecting.setId("Line");
        connecting.setStrokeLineCap(StrokeLineCap.ROUND);
        connecting.setStroke(Color.MIDNIGHTBLUE);
        connecting.setStrokeWidth(2.5);
        hbox.setOnMouseEntered(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
                //throw new UnsupportedOperationException("Not supported yet.");
                if (content.getId() != null) {

                    hbox.setStyle("-fx-border-color: Gold");
                    String[] splitforCoordinates = content.getId().split(",");
                    Double x = new Double(splitforCoordinates[0]);
                    Double y = new Double(splitforCoordinates[1]);
                    connecting.setLayoutX(x + 70);
                    connecting.setLayoutY(y + 60);
  
                    try {
                       
                    } catch (Exception e) {
                    }
                   
                } else {
                }
            }
        });

        hbox.setOnMouseExited(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
                hbox.setStyle("-fx-border-color: Transparent");
                Double xcoordinate = content.getLayoutX();
                Double ycoordinate = content.getLayoutY();
                TAITopology device = new TAITopology();           
                content.setId(xcoordinate.toString() + "," + ycoordinate.toString());
            }
        });



        hbox.setOnMouseClicked(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {

                if (anchorFlagSwitch == false) {

                    if (arg0.getClickCount() == 1) {

                        final Line con = new Line();
                        // connecting.setId("Line");
                        con.setStrokeLineCap(StrokeLineCap.ROUND);
                        con.setStroke(Color.MIDNIGHTBLUE);
                        con.setStrokeWidth(2.0);

                        final Line con1 = new Line();
                        con1.setStrokeLineCap(StrokeLineCap.ROUND);
                        con1.setStroke(Color.MIDNIGHTBLUE);
                        con1.setStrokeWidth(2.0);
                        final Line con2 = new Line();
                        con2.setStrokeLineCap(StrokeLineCap.ROUND);
                        con2.setStroke(Color.MIDNIGHTBLUE);
                        con2.setStrokeWidth(2.0);

                        final Line con3 = new Line();
                        con3.setStrokeLineCap(StrokeLineCap.ROUND);
                        con3.setStroke(Color.MIDNIGHTBLUE);
                        con3.setStrokeWidth(2.0);
                        final Anchor anchor3 = new Anchor("anchor3", con.startXProperty(), con.startYProperty());
                        final Anchor anchor4 = new Anchor("anchor4", con.endXProperty(), con.endYProperty());

                        final Anchor anchor5 = new Anchor("anchor5", con1.startXProperty(), con1.startYProperty());
                        final Anchor anchor6 = new Anchor("anchor6", con1.endXProperty(), con1.endYProperty());

                        final Anchor anchor7 = new Anchor("anchor7", con2.startXProperty(), con2.startYProperty());
                        final Anchor anchor8 = new Anchor("anchor8", con2.endXProperty(), con2.endYProperty());

                        final Anchor anchor9 = new Anchor("anchor9", con3.startXProperty(), con3.startYProperty());
                        final Anchor anchor10 = new Anchor("anchor10", con3.endXProperty(), con3.endYProperty());
                        anchor3.setLayoutX(content.getLayoutX());
                        anchor3.setLayoutY(content.getLayoutY());
                        anchor3.setVisible(false);
                        anchor4.setLayoutX(content.getLayoutX() + 40);
                        anchor4.setLayoutY(content.getLayoutY());

                        anchor5.setLayoutX(content.getLayoutX());
                        anchor5.setLayoutY(content.getLayoutY());
                        anchor5.setVisible(false);
                        anchor6.setLayoutX(content.getLayoutX() + 40);
                        anchor6.setLayoutY(content.getLayoutY() + 100);

                        anchor7.setLayoutX(content.getLayoutX());
                        anchor7.setLayoutY(content.getLayoutY());
                        anchor7.setVisible(false);
                        anchor8.setLayoutX(content.getLayoutX());
                        anchor8.setLayoutY(content.getLayoutY() + 50);
                        anchor9.setLayoutX(content.getLayoutX());
                        anchor9.setLayoutY(content.getLayoutY());
                        anchor9.setVisible(false);
                        //     anchor3.setId("anchor3");
                        //     anchor4.setId("anchor4");
                        anchor10.setLayoutX(content.getLayoutX() + 80);
                        anchor10.setLayoutY(content.getLayoutY() + 50);



                        // anchor5.setLayoutX(content.getLayoutX());
                        // anchor5.setLayoutY(content.getLayoutY());
                        // anchor5.setVisible(false);
                        // anchor6.setId("anchor6");
                        // anchor6.setLayoutX(content.getLayoutX());
                        // anchor6.setLayoutY(content.getLayoutY()+100);

                        con1.setLayoutX(anchor6.getLayoutX());
                        con1.setLayoutY(anchor6.getLayoutY());
                        con.setLayoutX(anchor4.getLayoutX());
                        con.setLayoutY(anchor4.getLayoutY());
                        con2.setLayoutX(anchor8.getLayoutX());
                        con2.setLayoutY(anchor8.getLayoutY());
                        con3.setLayoutX(anchor10.getLayoutX());
                        con3.setLayoutY(anchor10.getLayoutY());


                        con.setId("connectingLine");

                        con.setLayoutX(anchor4.getLayoutX());
                        con.setLayoutY(anchor4.getLayoutY());



                        anchorFlagSwitch = true;
                        
                       
                        hb.getChildren().addAll(con, anchor3, anchor4, con1, anchor5, anchor6, con2, anchor7, anchor8, con3, anchor9, anchor10);
                        final ArrayList<Node> removeNodes = new ArrayList<Node>();
                   
                         
                         
                        closeButton.setOnAction(new EventHandler<ActionEvent>() {

                            @Override
                            public void handle(ActionEvent t) {
                                //throw new UnsupportedOperationException("Not supported yet.");
                                
                                                Node parent = hbox.getParent();
                ObservableList<Node> allCurrentNode = hb.getChildren();



                for (Node node : allCurrentNode) {
                    if (node.toString().contains("Line")) {
                        if (!node.toString().matches("Line[id=Line[id=null,null]]")) {
                           
                            if (node.getId() != null) {
                                String[] startLineNode = node.getId().split(",");

                                Integer nodeHash = content.hashCode();
                                if (nodeHash.toString().equals(startLineNode[0])) {
                                    removeNodes.add(node);

                                }
                                if (startLineNode.length == 2) {
                                    if (nodeHash.toString().equals(startLineNode[1])) {

                                        removeNodes.add(node);

                                    }
                                }
                            }

                        }   
                    }
                }

                for (Node removenode : removeNodes) {
                    hb.getChildren().remove(removenode);
                                  
                }
                hb.getChildren().remove(content);
                                
                                  anchorFlagSwitch = false;
                                  hb.getChildren().removeAll(con, anchor3, anchor4, con1, anchor5, anchor6, con2, anchor7, anchor8, con3, anchor9, anchor10);
                            }
                        });
                        final ObservableList<Node> allNodeInCanvas = hb.getChildren();

  HashMap<Node,String> anchorNodeHash = new HashMap();
  anchorNodeHash.put(anchor4,anchor4.getId());
  anchorNodeHash.put(anchor6, anchor6.getId());
  anchorNodeHash.put(anchor8, anchor8.getId());
  anchorNodeHash.put(anchor10, anchor10.getId());
  anchorNodeHash.put(con1, con1.getId());
  anchorNodeHash.put(con2, con2.getId());
  anchorNodeHash.put(con3, con3.getId());
  anchorNodeHash.put(con, con.getId());
                   
                        anchorsInsideImageNode(anchor4, 40, 50, hb, content, hbox, con,anchorNodeHash);

                        anchorsInsideImageNode(anchor6, 40, 50, hb, content, hbox, con1,anchorNodeHash);

                        anchorsInsideImageNode(anchor8, 40, 50, hb, content, hbox, con2,anchorNodeHash);

                        anchorsInsideImageNode(anchor10, 40, 50, hb, content, hbox, con3,anchorNodeHash);

                      
                                                        
                          
                        hbox.setOnDragDetected(new EventHandler<MouseEvent>() {

                            @Override
                            public void handle(MouseEvent t) {
                                //throw new UnsupportedOperationException("Not supported yet.");
                                hbox.startFullDrag();
                            }
                        });


                        hbox.setOnMouseDragged(new EventHandler<MouseEvent>() {

                            @Override
                            public void handle(MouseEvent t) {
                                anchorFlagSwitch = false;
                                hb.getChildren().removeAll(con, con1, con2, con3, anchor4, anchor6, anchor8, anchor10);
                            }
                        });

                        hbox.setOnMouseMoved(new EventHandler<MouseEvent>() {

                            @Override
                            public void handle(MouseEvent arg0) {
                                boolean exitFlag = false;
                                for (int i = 0; i <= 80; i++) {
                                    for (int j = 0; j <= 100; j++) {
                                        Double x1 = content.getLayoutX() + 482.0;
                                        Double y1 = content.getLayoutY() + 142.0;
                                        Double x11 = x1 + i;
                                        Double y11 = y1 + j;
                                        if (x11 == arg0.getSceneX()) {
                                            if (y11 == arg0.getSceneY()) {
                                                exitFlag = true;

                                            }
                                        }
                                    }
                                }
                                if (exitFlag == false) {
                                    hbox.setStyle("-fx-border-color: Transparent");
                                    anchorFlagSwitch = false;
                                    hb.getChildren().removeAll(con, con1, con2, con3, anchor4, anchor5, anchor6, anchor7, anchor8, anchor9, anchor10);
                                }


                            }
                        });




                        hbox.setOnMouseExited(new EventHandler<MouseEvent>() {

                            @Override
                            public void handle(MouseEvent arg0) {
                                // throw new UnsupportedOperationException("Not supported yet.");
                                boolean exitFlag = false;
                                for (int i = 0; i <= 80; i++) {
                                    for (int j = 0; j <= 100; j++) {
                                        Double x1 = content.getLayoutX() + 482.0;
                                        Double y1 = content.getLayoutY() + 142.0;
                                        Double x11 = x1 + i;
                                        Double y11 = y1 + j;
                                        if (x11 == arg0.getSceneX()) {
                                            if (y11 == arg0.getSceneY()) {
                                                exitFlag = true;

                                            }
                                          
                                        }
                                       
                                    }
                                }
                                if (exitFlag == false) {
                                    hbox.setStyle("-fx-border-color: Transparent");
                                    anchor4.setVisible(false);
                                    con.setVisible(false);
                                    anchor6.setVisible(false);
                                    con1.setVisible(false);
                                    anchor8.setVisible(false);
                                    con2.setVisible(false);
                                    anchor10.setVisible(false);
                                    con3.setVisible(false);
                                    anchorFlagSwitch = false;
                                    hb.getChildren().removeAll(anchor3, anchor4, anchor5, anchor6, anchor7, anchor8, anchor9, anchor10, con, con1, con2, con3);
                                }
                            }
                        });

                    }
                    
                }

                if (arg0.getClickCount() == 2) {

                    if (deviceParent.equals("emulator")||deviceParent.equals("tool")||deviceParent.equals("remotesys")||deviceParent.equals("")) {

                        try {

                            String setHost = null, setUser = null, setPassword = null, setTransport = null, setPort = null;
                            File fileName = new File(OFAReference.editorTabPane.getSelectionModel().getSelectedItem().getId());
                            String tabName = fileName.getName();
                            if (tabName.equals(OFAReference.editorTabPane.getSelectionModel().getSelectedItem().getText())) {
                                OFAReference.editorTabPane.getSelectionModel().getSelectedItem().setText("* " + OFAReference.editorTabPane.getSelectionModel().getSelectedItem().getText());
                            }

                            topoplogy = new TAITopology();
                            topoplogy.start(new Stage());
                            for (String hostName : tplObject.getHostName()) {
                                if (hostName.equals(tplObject.getdeviceNameAndHost().get(txt))) {
                                    topoplogy.hostNameText.setText(hostName.replaceAll("\\s+", ""));
                                    setHost = hostName.replaceAll("\\s+", "");
                                }
                            }
                            for (String user : tplObject.getUserName()) {
                                if (user.equals(tplObject.getdeviceNameAndUser().get(txt))) {
                                    topoplogy.userNameText.setText(user.replaceAll("\\s+", ""));
                                    setUser = user.replaceAll("\\s+", "");
                                }
                            }

                            for (String password : tplObject.getPassword()) {
                                if (password.equals(tplObject.getdeviceNameAndPassword().get(txt))) {
                                    topoplogy.passwordText.setText(password.replaceAll("\\s+", ""));
                                    setPassword = password.replaceAll("\\s+", "");
                                }
                            }
                            TAIParseTplFile dynamicParseTplObject = new TAIParseTplFile();
                            Hashtable interfaceHash;
                            interfaceHash = dynamicParseTplObject.parseTpl(tplFilePath, txt, deviceParent);

                            Set set = interfaceHash.entrySet();
                            Iterator interfaceTopoHashIterator = set.iterator();
                            while (interfaceTopoHashIterator.hasNext()) {
                                Map.Entry interfaceKeyValues = (Map.Entry) interfaceTopoHashIterator.next();

                                topoplogy.attributeText.setText(interfaceKeyValues.getKey().toString().replaceAll("\\s+", ""));
                                topoplogy.valueText.setText(interfaceKeyValues.getValue().toString().replaceAll("\\s+", ""));
                                topoplogy.addInterFace();
                            }


                        } catch (Exception ex) {
                            Logger.getLogger(TopologyWizard.class.getName()).log(Level.SEVERE, null, ex);
                        }

                        topoplogy.save.setOnAction(new EventHandler<ActionEvent>() {

                            @Override
                            public void handle(ActionEvent arg0) {

                                topoplogy.getHostName = topoplogy.hostNameText.getText();
                                topoplogy.getUserName = topoplogy.userNameText.getText();
                                topoplogy.getPassword = topoplogy.passwordText.getText();

                                for (int i = 0; i < topoplogy.deviceTable.getItems().size(); i++) {
                                    topoplogy.deviceTable.getSelectionModel().select(i);
                                    interFaceHashDetail.put(topoplogy.deviceTable.getSelectionModel().getSelectedItem().getDeviceName().getText(), topoplogy.deviceTable.getSelectionModel().getSelectedItem().getDeviceType().getText() + "_" + text.getText());
                                    arrayOfInterFaceHash = new ArrayList<TreeMap<String, String>>();
                                    arrayOfInterFaceHash.add(interFaceHashDetail);
                                }

                                if (!getPropertyDetail().isEmpty()) {
                                    try {
                                        for (String checkBeforeAdding : getPropertyDetail()) {


                                            if (checkBeforeAdding.contains(text.getText())) {
                                                getPropertyDetail().remove(checkBeforeAdding);

                                                propertyValue.add(text.getText() + "\n" + topoplogy.getHostName + "\n" + topoplogy.getUserName + "\n" + topoplogy.getPassword + "\n" + topoplogy.getTranportProtocol + "\n" + deviceName + "\n" + topoplogy.getPort + "\n" + content.getId());
                                                topoplogy.copyStage.close();
                                            } else {

                                                propertyValue.add(text.getText() + "\n" + topoplogy.getHostName + "\n" + topoplogy.getUserName + "\n" + topoplogy.getPassword + "\n" + topoplogy.getTranportProtocol + "\n" + deviceName + "\n" + topoplogy.getPort + "\n" + content.getId());
                                                topoplogy.copyStage.close();
                                            }

                                        }
                                    } catch (Exception e) {
                                    }



                                } else {

                                    propertyValue.add(text.getText() + "\n" + topoplogy.getHostName + "\n" + topoplogy.getUserName + "\n" + topoplogy.getPassword + "\n" + topoplogy.getTranportProtocol + "\n" + deviceName + "\n" + topoplogy.getPort + "\n" + content.getId());
                                    topoplogy.copyStage.close();
                                }



                                // throw new UnsupportedOperationException("Not supported yet.");


                            }
                        });
                        topoplogy.cancelButton.setOnAction(new EventHandler<ActionEvent>() {

                            @Override
                            public void handle(ActionEvent arg0) {
                                topoplogy.copyStage.close();
                            }
                        });
                        topoplogy.defaultButton.setOnAction(new EventHandler<ActionEvent>() {

                            @Override
                            public void handle(ActionEvent arg0) {
                                //throw new UnsupportedOperationException("Not supported yet.");
                                for (String hostName : tplObject.getHostName()) {
                                    if (hostName.equals(tplObject.getdeviceNameAndHost().get(txt))) {
                                        topoplogy.hostNameText.setText(hostName);
                                    }
                                }
                                for (String user : tplObject.getUserName()) {
                                    if (user.equals(tplObject.getdeviceNameAndUser().get(txt))) {
                                        topoplogy.userNameText.setText(user);
                                    }
                                }

                                for (String password : tplObject.getPassword()) {
                                    if (password.equals(tplObject.getdeviceNameAndPassword().get(txt))) {
                                        topoplogy.passwordText.setText(password);
                                    }
                                }

                                for (String transport : tplObject.getTransport()) {
                                    if (transport.equals(tplObject.getdeviceNameAndTransport().get(txt))) {
                                        topoplogy.transportList.setEditable(true);
                                        topoplogy.transportList.getSelectionModel().select(transport);
                                    }
                                }

                                for (String port : tplObject.getPort()) {
                                    if (port.equals(tplObject.getdeviceNameAndPort().get(txt))) {
                                        topoplogy.portText.setText(port);
                                    }
                                }
                            }
                        });

                    } 

                    OFAReference.Save.setOnAction(new EventHandler<ActionEvent>() {

                        @Override
                        public void handle(ActionEvent arg0) {
                            //throw new UnsupportedOperationException("Not supported yet.");
                            File currentTabPath = new File(OFAReference.editorTabPane.getSelectionModel().getSelectedItem().getId());
                            OFAReference.editorTabPane.getSelectionModel().getSelectedItem().setText(currentTabPath.getName());

                            ArrayList<String> deviceName = new ArrayList<String>();
                            Iterator<TextField> attributeIterator = getDeviceNameList().iterator();
                            while (attributeIterator.hasNext()) {
                                TextField iteratorAttributeText = attributeIterator.next();
                                deviceName.add(iteratorAttributeText.getText());
                            }

                            String topologyFileDemo = "<TOPOLOGY>" + "\n\t" + "<COMPONENT>" + "\n\t";
                 
                            for (String device : getPropertyDetail()) {
                                String[] splitDeviceDetail = device.split("\n");
                                topologyFileDemo += "\n\t\t" + "<" + splitDeviceDetail[0] + ">";
                           
                                splitDeviceDetail = device.split("\n");
                                Hashtable tempHash = new Hashtable();
                                try {
                                    
                                    tempHash.put("hostname", splitDeviceDetail[1]);
                                    tempHash.put("user", splitDeviceDetail[2]);
                                    tempHash.put("password", splitDeviceDetail[3]);
                                    tempHash.put("transport",splitDeviceDetail[4]);
                                    tempHash.put("type",splitDeviceDetail[5]);
                                    tempHash.put("coordinate",splitDeviceDetail[6]);
                                    tempHash.put("coordinate",splitDeviceDetail[7]);
                                    
                                    
                                    
                                    topologyFileDemo += "\n\t\t\t" + "<hostname>" + splitDeviceDetail[1] +   "</hostname>" +"\n\t\t\t" + "<user>" + splitDeviceDetail[2] +
                                            "</user>"
                                            + "\n\t\t\t" + "<password>" + splitDeviceDetail[3] + "</password>"+ "\n\t\t\t" + "<transport>" + splitDeviceDetail[4] + "</transport>"+"\n\t\t\t" 
                                            + "\n\t\t\t" + "<type>" + splitDeviceDetail[5] + "</type>" +"\n\t\t\t" + "<coordinate>" + splitDeviceDetail[7] + "</coordinate>";
                                    String[] deviceDetailsArray = interFaceValue.toArray(new String[interFaceValue.size()]);
                                    topologyFileDemo +=  "\n\t\t\t\t" + "<COMPONENTS>";
                                    int noOfDevices = 0;
                                    for (String name : interFaceName) {
                                        String propertyDetail = deviceDetailsArray[noOfDevices++];
                                        String[] details = propertyDetail.split("\\_");
                                        String[] splitInterFace = name.split("\\_");
                                        if (splitInterFace[1].equals(splitDeviceDetail[0]) && details[1].equals(splitDeviceDetail[0])) {
                                            //              topologyFileDemo +=  "\n\t\t\t"+splitInterFace[0]+"="+details[0];
                                        }
                                    }
                                    for (TreeMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
                                        Set set = interFaceDetail.entrySet();
                                        Iterator interFaceHashDetailIterator = set.iterator();
                                        while (interFaceHashDetailIterator.hasNext()) {
                                            Map.Entry me = (Map.Entry) interFaceHashDetailIterator.next();
                                            String[] deviceNameAndiniterFaceValue = me.getValue().toString().split("\\_");
                                            if (deviceNameAndiniterFaceValue[1].equals(splitDeviceDetail[0])) {
                                                if (!me.getKey().toString().isEmpty()) {
                                                    if (!me.getKey().toString().equals("//s+")) {
                                                        tempHash.put(me.getKey().toString(),me.getValue().toString());
                                                        topologyFileDemo += "\n\t\t\t" + "<" + me.getKey().toString() + ">" + deviceNameAndiniterFaceValue[0].toString() + "</" + me.getKey().toString() + ">";
                                                    }
                                                }
                                            }

                                        }
                                    }
                                    
                                    topologyFileDemo +=  "\n\t\t\t\t" + "</COMPONENTS>";
                                    topologyFileDemo += "\n\t\t" + "</" + splitDeviceDetail[0] + ">";
                                    modifyHash.put(splitDeviceDetail[0], tempHash); 
                                } catch (Exception e) {
                                }

                            }
                            // for(HashMap<String,String> writeLink:arrayOfLinkTopologyHash){

                            Set set = linkTopologyHash.entrySet();
                            Iterator linkHashDetailIterator = set.iterator();
                            while (linkHashDetailIterator.hasNext()) {
                                Map.Entry me = (Map.Entry) linkHashDetailIterator.next();

                                String[] linkValue = me.getValue().toString().split("_");
                                String[] linkCoordinates = me.getKey().toString().split("_");
                                //if (deviceNameAndiniterFaceValue[1].equals(splitDeviceDetail[0])) {
                                // if (!me.getKey().toString().isEmpty()) {
                                //    if (!me.getKey().toString().equals("//s+")) {
                                topologyFileDemo += "\n\t\t" + "<" + linkValue[0] + ">";
                                topologyFileDemo += "\n\t\t\t" + "<" + linkValue[2].toString() + ">" + linkValue[3].toString()  + "</" + linkValue[2].toString() + ">";
                                topologyFileDemo += "\n\t\t\t" + "<"+linkValue[4].toString() + ">" + linkValue[5].toString() + "</"+linkValue[4].toString() + ">";

                                topologyFileDemo += "\n\t\t\t" + "<linkCoordinates" + ">" + linkCoordinates[1].toString() + "," + linkCoordinates[2] + "," + linkCoordinates[3] + "," + linkCoordinates[4] + 
                                         "</linkCoordinates" + ">";
                                topologyFileDemo += "\n\t\t" + "</" + linkValue[0] + ">";
                                
                            }

                            topologyFileDemo += "\n\t" + "</COMPONENT>" + "\n" + "</TOPOLOGY>";
                            TAIParseTplFile tplFileParseForLink = new TAIParseTplFile();
                            Hashtable deviceHash = new Hashtable();
                            deviceHash = tplFileParseForLink.getDeviceHash(tplFilePath);
                            Set<String> keys = modifyHash.keySet();
                            for(String key: keys){
                               if (deviceHash.containsKey(key)){
                                   deviceHash.put(key,modifyHash.get(key) );
                                   
                               }else if (!deviceHash.containsKey(key)){
                                  deviceHash.put(key,modifyHash.get(key) );  
                               } 
                               
                            }
                            writeInFile(tplFilePath, topologyFileDemo);

                        }
                    });

                }
                
            }
        });
      
         final ArrayList<Node> removeNodes = new ArrayList<Node>();
         
        closeActionForAnchorsRemoval(closeButton, hbox, removeNodes, content); 
        HBox box = new HBox();
        final StackPane pane = new StackPane();
        Button lineButton = new Button("Line");
        lineButton.setAlignment(Pos.CENTER);
        lineButton.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent arg0) {
                //throw new UnsupportedOperationException("Not supported yet.");
                connecting.setId("Line");
                connecting.setStrokeLineCap(StrokeLineCap.ROUND);
                connecting.setStroke(Color.MIDNIGHTBLUE);
                connecting.setStrokeWidth(2);


                final TopologyNode.Anchor anchor2 = new TopologyNode.Anchor("Anchor 2", connecting.endXProperty(), connecting.endYProperty());
                Circle[] circles = {anchor2};
                for (Circle circle : circles) {
                    enableDrag(circle);
                }

                hb.getChildren().addAll(connecting);

            }
        });
        HBox imageAndLineButton = new HBox();
        pane.getChildren().add(iv);
        hor.getChildren().add(iv);
        hbox.getChildren().addAll(closeButton, iv, text);
        hbox.setId(iv.toString());
        text.setPromptText("Device Name");
        content.getChildren().add(hbox);
        content.setOnMouseExited(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
                //throw new UnsupportedOperationException("Not supported yet.");
                Double xcoordinate = content.getLayoutX();
                Double ycoordinate = content.getLayoutY();
                TAITopology device = new TAITopology();
                content.setId(xcoordinate.toString() + "," + ycoordinate.toString());

            }
        });

        content.setLayoutX(x);
        content.setLayoutY(y);
        insertedDeviceNameAndCoordinatesHash.put(content, x + "," + y + "," + txt);
        hb.getChildren().add(content);
    }

    public ArrayList<String> getPropertyDetail() {
        return propertyValue;
    }

    void anchorsInsideImageNode(final Anchor anchor, final double bindLinex, final double bindLiney, final Pane hb, final DraggableNode content, final VBox hbox, final Line con,final HashMap<Node,String> anchorNodeHash) {


        final Line con11 = new Line();

        anchor.setOnDragDetected(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
                //     throw new UnsupportedOperationException("Not supported yet.");
                anchor.startFullDrag();
                enableDrag(anchor);
            }
        });


        hbox.setOnDragDetected(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
                //throw new UnsupportedOperationException("Not supported yet.");
                hbox.startFullDrag();
                anchor.setVisible(false);
                con.setVisible(false);
            }
        });

        hbox.setOnMouseDragReleased(new EventHandler<MouseDragEvent>() {

            @Override
            public void handle(MouseDragEvent arg0) {
    
                anchor.setVisible(false);
                con.setVisible(false);
            }
        });


        hbox.setOnMouseDragged(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
              
                try {
                    con.setVisible(false);
                    anchor.setVisible(false);
                    hb.getChildren().removeAll(con, anchor);
                } catch (Exception e) {
                }

            }
        });


        anchor.setOnMouseDragReleased(new EventHandler<MouseDragEvent>() {

            @Override
            public void handle(MouseDragEvent arg0) {
                ObservableList<Node> allNodesCanvas = hb.getChildren();
                boolean flag = false;
                String startBind = null;
                String endBind = null;
                try {
                    for (Node node : allNodesCanvas) {
                        Double x = node.getLayoutX() + 482.0;
                        Double y = node.getLayoutY() + 142.0;
                        
                        for (int i = 0; i <= 80; i++) {
                            for (int j = 0; j <= 100; j++) {
                                Double x1 = node.getLayoutX() + 482.0;
                                Double y1 = node.getLayoutY() + 142.0;
                                Double x11 = x1 + i;
                                Double y11 = y1 + j;
                                if (x11 == arg0.getSceneX()) {
                                    if (y11 == arg0.getSceneY()) {
                                     con11.setStrokeLineCap(StrokeLineCap.ROUND);
                                        con11.setStroke(Color.MIDNIGHTBLUE);
                                        con11.setStrokeWidth(2.0);
                                        con11.startXProperty().bind(content.layoutXProperty().add(bindLinex));
                                        con11.startYProperty().bind(content.layoutYProperty().add(bindLiney));
                                        startBind = ((Integer) content.hashCode()).toString();
                                        con11.endXProperty().bind(node.layoutXProperty().add(bindLinex));
                                        con11.endYProperty().bind(node.layoutYProperty().add(bindLiney));
                                        endBind = ((Integer) node.hashCode()).toString();
                                        con11.setVisible(true);
                                        hbox.setStyle("-fx-border-color: Transparent");
                                        hb.getChildren().add(con11);
                                        con.setVisible(false);
                                        anchor.setVisible(false);
                                      
                                        flag = true;
                                        Map<Node, String> map = anchorNodeHash;
                                        Iterator<Map.Entry<Node, String>> entries = map.entrySet().iterator();
                                        while (entries.hasNext()) {
                                            Map.Entry<Node, String> entry = entries.next();
                                            entry.getKey();
                                            hb.getChildren().remove(entry.getKey());
                                            anchorFlagSwitch = false;
                                        }
                                        con11.setId(startBind + "," + endBind);

                                    }

                                }
                            }
                        }

                    }
                    if (flag == false) {
                        con.setVisible(false);
                        anchor.setVisible(false);
                          Map<Node, String> map = anchorNodeHash;
                                        Iterator<Map.Entry<Node, String>> entries = map.entrySet().iterator();
                                        while (entries.hasNext()) {
                                            Map.Entry<Node, String> entry = entries.next();
                                            entry.getKey();
                                            hb.getChildren().remove(entry.getKey());
                                            anchorFlagSwitch = false;
                                            
                                            
                                        }
                        
                        
                    }
                } catch (Exception e) {
                }
            }
        });

        con11.setOnMouseEntered(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
                con11.setStroke(Color.GOLD);
            }
        });
        con11.setOnMouseExited(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
             
                con11.setStroke(Color.MIDNIGHTBLUE);
            }
        });
       
        final DraggableNode contentLine = new DraggableNode();

        con11.setOnMouseClicked(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent arg0) {
                if (arg0.getClickCount() == 2) {
                     
                    topologyLink.start(new Stage());
                    if (!arrayOfLinkTopologyHash.isEmpty()) {
                        for (HashMap<String, String> linkHash : arrayOfLinkTopologyHash) {
                            Set linkSet = linkHash.entrySet();
                            Iterator linkHashDetailIterator = linkSet.iterator();
                            while (linkHashDetailIterator.hasNext()) {
                                
                                Map.Entry linkMap = (Map.Entry) linkHashDetailIterator.next();

                                if (linkMap.getKey().toString().equals(connecting.getId())) {
                                    String[] linkValues = linkMap.getValue().toString().split("_");
                                    topologyLink.nameText.setText(linkValues[0]);
                                    topologyLink.typeText.setText(linkValues[1]);
                                    topologyLink.devicesInTopoEditor.setEditable(true);
                                    topologyLink.devicesInTopoEditor.getSelectionModel().select(linkValues[2]);
                                    topologyLink.interfaceList2.setEditable(true);
                                    topologyLink.interfaceList2.getSelectionModel().select(linkValues[3]);
                                    topologyLink.destDevicesInTopoEditor.setEditable(true);
                                    topologyLink.destDevicesInTopoEditor.getSelectionModel().select(linkValues[4]);
                                    topologyLink.interfaceList4.setEditable(true);
                                    topologyLink.interfaceList4.getSelectionModel().select(linkValues[5]);
                                    
                                }



                            }

                        }
                    }

                    for (String string : topoEditorDeviceInfo) {
                        topologyLink.devicesInTopoEditor.getItems().add(string);
                        topologyLink.destDevicesInTopoEditor.getItems().add(string);
                    }


                    topologyLink.devicesInTopoEditor.setOnAction(new EventHandler<ActionEvent>() {

                        @Override
                        public void handle(ActionEvent arg0) {
                            
                            try {
                             
                                for (TreeMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
                                    Set set = interFaceDetail.entrySet();
                                    Iterator interFaceHashDetailIterator = set.iterator();
                                    while (interFaceHashDetailIterator.hasNext()) {
                                        Map.Entry me = (Map.Entry) interFaceHashDetailIterator.next();
                                        String[] deviceNameAndiniterFaceValue = me.getValue().toString().split("\\_");


                                        if (deviceNameAndiniterFaceValue[1].equals(topologyLink.devicesInTopoEditor.getSelectionModel().getSelectedItem())) {
                                            //  topologyLink.interfaceList2.getItems().clear();  
                                            if (!me.getKey().toString().equals("")) {
                                                topologyLink.interfaceList2.getItems().add(me.getKey().toString());

                                            }
                                        }
                                    }
                                }
                            } catch (Exception e) {
                            }
                        }
                    });

                    topologyLink.destDevicesInTopoEditor.setOnAction(new EventHandler<ActionEvent>() {

                        @Override
                        public void handle(ActionEvent arg0) {

                            topologyLink.interfaceList4.getItems().clear();
                            try {
                                for (TreeMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
                                    Set set = interFaceDetail.entrySet();
                                    Iterator interFaceHashDetailIterator = set.iterator();
                                    while (interFaceHashDetailIterator.hasNext()) {
                                        Map.Entry me = (Map.Entry) interFaceHashDetailIterator.next();


                                        String[] deviceNameAndiniterFaceValue = me.getValue().toString().split("\\_");
                                        if (deviceNameAndiniterFaceValue[1].equals(topologyLink.destDevicesInTopoEditor.getSelectionModel().getSelectedItem())) {
                                            if (!me.getKey().toString().equals("")) {                            
                                                topologyLink.interfaceList4.getItems().add(me.getKey().toString());
                                            }
                                        }

                                    }
                                }
                            } catch (Exception e) {
                            }
                        }
                    });
                    
                    topologyLink.finishSelectedLink.setOnAction(new EventHandler<ActionEvent>() {

                        @Override
                        public void handle(ActionEvent arg0) {                         
                            con11.setId(topologyLink.nameText.getText() + "_" + con11.getStartX() + "_" + con11.getStartY() + "_" + con11.getEndX() + "_" + con11.getEndY());
                            String detailedString = topologyLink.nameText.getText() + "_" + topologyLink.typeText.getText() + "_" + topologyLink.devicesInTopoEditor.getSelectionModel().getSelectedItem() + "_" + topologyLink.interfaceList2.getSelectionModel().getSelectedItem() + "_" + topologyLink.destDevicesInTopoEditor.getSelectionModel().getSelectedItem() + "_" + topologyLink.interfaceList4.getSelectionModel().getSelectedItem() + "_";
                            linkTopologyHash.put(con11.getId(), detailedString);
                            arrayOfLinkTopologyHash.add(linkTopologyHash);
                            topologyLink.copyStage.close();
                        }
                    });
                    topologyLink.cancelButton.setOnAction(new EventHandler<ActionEvent>() {

                        @Override
                        public void handle(ActionEvent arg0) {
                            topologyLink.copyStage.close();
                        }
                    });


                } else if (arg0.getButton() == MouseButton.SECONDARY) {

                    deleteLineContextMenu(contentLine, con11, arg0);

                }
            }
        });

    }

    void insertLine(String tplFilePath, Pane hPane, final String linkName) {
        TAIParseTplFile tplFileParseForLink = new TAIParseTplFile();
        Hashtable linkDetails = tplFileParseForLink.parseLinkTpl(tplFilePath, linkName);
        if(linkDetails != null ){
            Set linkset = linkDetails.entrySet();
        final ArrayList<String> getOtherLinkParameters = new ArrayList<String>();
        Iterator linkHashDetailIterator = linkset.iterator();
        while (linkHashDetailIterator.hasNext()) {
            Map.Entry me = (Map.Entry) linkHashDetailIterator.next();
            Pane canvasPane = (Pane) canvasTab.getContent();
            ObservableList<Node> anchorNode = canvasPane.getChildren();
            final Line connect = new Line();

            if (me.getKey().toString().replaceAll("\\s", "").equals("linkCoordinates")) {

                String[] linkCoordinates = me.getValue().toString().replaceAll("\\s", "").split("\\,");
                connect.setId("Line");
                connect.setStrokeLineCap(StrokeLineCap.ROUND);
                connect.setStroke(Color.MIDNIGHTBLUE);
                connect.setStrokeWidth(2.0);

                connect.setStartX(new Double(linkCoordinates[0]));
                connect.setStartY(new Double(linkCoordinates[1]));
                connect.setEndX(new Double(linkCoordinates[2]));
                connect.setEndY(new Double(linkCoordinates[3]));

                Set nodeAndCoordinateset = insertedDeviceNameAndCoordinatesHash.entrySet();
                Iterator nodeTopoHashIterator = nodeAndCoordinateset.iterator();

            } else {

                getOtherLinkParameters.add(me.getKey().toString().replaceAll("\\s", ""));
            }


             String startx = null;
             String starty = null;

            final Anchor anchor1 = new Anchor("Anchor 1", connect.startXProperty(), connect.startYProperty());
            final Anchor anchor2 = new Anchor("Anchor 2", connect.endXProperty(), connect.endYProperty());
            Circle[] circles = {anchor1, anchor2};
            for (Circle circle : circles) {
                enableDrag(circle);
            }
            Set nodeAndCoordinateset = insertedDeviceNameAndCoordinatesHash.entrySet();
            Iterator nodeTopoHashIterator = nodeAndCoordinateset.iterator();
            while (nodeTopoHashIterator.hasNext()) {
                Map.Entry nodeCoordinateEntry = (Map.Entry) nodeTopoHashIterator.next();
                Node node = (Node) nodeCoordinateEntry.getKey();

                for (int i = 0; i <= 80; i++) {
                    for (int j = 0; j <= 100; j++) {
                        Double x11 = node.getLayoutX() + i;
                        Double y11 = node.getLayoutY() + j;
                        if (x11 == connect.getStartX()) {
                            if (y11 == connect.getStartY()) {
                                connect.startXProperty().bind(node.layoutXProperty().add(40));
                                connect.startYProperty().bind(node.layoutYProperty().add(50));
                                startx = ((Integer)node.hashCode()).toString();
                            }
                        }
                        if (x11 == connect.getEndX()) {
                            if (y11 == connect.getEndY()) {
                                connect.endXProperty().bind(node.layoutXProperty().add(40));
                                connect.endYProperty().bind(node.layoutYProperty().add(50));
                                starty = ((Integer)node.hashCode()).toString();
                            }
                        }
                    }
                }

            }
            connect.setId(startx+","+starty);

            anchor1.setFill(Color.TRANSPARENT.deriveColor(1, 1, 1, 0.5));
            anchor2.setFill(Color.TRANSPARENT.deriveColor(1, 1, 1, 0.5));
            anchor1.setVisible(false);
            anchor2.setVisible(false);
            anchor1.setOnMouseEntered(new EventHandler<MouseEvent>() {

                @Override
                public void handle(MouseEvent arg0) {
                    anchor1.setFill(Color.GOLD.deriveColor(1, 1, 1, 0.5));
                    anchor1.setVisible(true);
                    anchor2.setVisible(true);
                }
            });

            anchor1.setOnMouseExited(new EventHandler<MouseEvent>() {

                @Override
                public void handle(MouseEvent arg0) {
                    anchor1.setFill(Color.TRANSPARENT.deriveColor(1, 1, 1, 0.5));
                    anchor1.setVisible(false);
                    anchor2.setVisible(false);
                }
            });

            anchor2.setOnMouseEntered(new EventHandler<MouseEvent>() {

                @Override
                public void handle(MouseEvent arg0) {
                    anchor2.setFill(Color.GOLD.deriveColor(1, 1, 1, 0.5));
                    anchor1.setVisible(true);
                    anchor2.setVisible(true);
                }
            });
            anchor2.setOnMouseExited(new EventHandler<MouseEvent>() {

                @Override
                public void handle(MouseEvent arg0) {
                    anchor2.setFill(Color.TRANSPARENT.deriveColor(1, 1, 1, 0.5));
                    anchor1.setVisible(false);
                    anchor2.setVisible(false);
                }
            });

            connect.setOnMouseClicked(new EventHandler<MouseEvent>() {

                @Override
                public void handle(MouseEvent arg0) {
                    if (arg0.getClickCount() == 2) {

                        topologyLink.start(new Stage());
                        if (!arrayOfLinkTopologyHash.isEmpty()) {
                            for (HashMap<String, String> linkHash : arrayOfLinkTopologyHash) {
                                Set linkSet = linkHash.entrySet();
                                Iterator linkHashDetailIterator = linkSet.iterator();
                                while (linkHashDetailIterator.hasNext()) {
                                    Map.Entry linkMap = (Map.Entry) linkHashDetailIterator.next();
                                    if (linkMap.getKey().toString().equals(connecting.getId())) {
                                        String[] linkValues = linkMap.getValue().toString().split("_");

                                        topologyLink.nameText.setText(linkValues[0]);
                                        topologyLink.typeText.setText(linkValues[1]);
                                        topologyLink.devicesInTopoEditor.setEditable(true);
                                        topologyLink.devicesInTopoEditor.getSelectionModel().select(linkValues[2]);
                                        topologyLink.interfaceList2.setEditable(true);
                                        topologyLink.interfaceList2.getSelectionModel().select(linkValues[3]);
                                        topologyLink.destDevicesInTopoEditor.setEditable(true);
                                        topologyLink.destDevicesInTopoEditor.getSelectionModel().select(linkValues[4]);
                                        topologyLink.interfaceList4.setEditable(true);
                                        topologyLink.interfaceList4.getSelectionModel().select(linkValues[5]);
                                    }

                                }

                            }
                        } else {
                            topologyLink.nameText.setText(linkName);
                            topologyLink.typeText.setText("");
                            topologyLink.devicesInTopoEditor.setEditable(true);
                            topologyLink.devicesInTopoEditor.getSelectionModel().select(getOtherLinkParameters.get(0));
                            topologyLink.interfaceList2.setEditable(true);
                            topologyLink.interfaceList2.getSelectionModel().select(getOtherLinkParameters.get(1));
                            topologyLink.destDevicesInTopoEditor.setEditable(true);
                            topologyLink.destDevicesInTopoEditor.getSelectionModel().select(getOtherLinkParameters.get(1));
                            topologyLink.interfaceList4.setEditable(true);
                         
                        }

                        for (String string : topoEditorDeviceInfo) {
                            topologyLink.devicesInTopoEditor.getItems().add(string);
                            topologyLink.destDevicesInTopoEditor.getItems().add(string);
                        }

                        topologyLink.devicesInTopoEditor.setOnAction(new EventHandler<ActionEvent>() {

                            @Override
                            public void handle(ActionEvent arg0) {
                                //throw new UnsupportedOperationException("Not supported yet.");
                                topologyLink.interfaceList2.getItems().clear();
                                try {
                                    for (TreeMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
                                        Set set = interFaceDetail.entrySet();
                                        Iterator interFaceHashDetailIterator = set.iterator();
                                        while (interFaceHashDetailIterator.hasNext()) {
                                            Map.Entry me = (Map.Entry) interFaceHashDetailIterator.next();

                                            String[] deviceNameAndiniterFaceValue = me.getValue().toString().split("\\_");
                                            if (deviceNameAndiniterFaceValue[1].equals(topologyLink.devicesInTopoEditor.getSelectionModel().getSelectedItem())) {
                                                if (!me.getKey().toString().equals("")) {
                                                    topologyLink.interfaceList2.getItems().add(me.getKey().toString());

                                                }
                                            }
                                        }
                                    }
                                } catch (Exception e) {
                                }
                            }
                        });

                        topologyLink.destDevicesInTopoEditor.setOnAction(new EventHandler<ActionEvent>() {

                            @Override
                            public void handle(ActionEvent arg0) {

                                topologyLink.interfaceList4.getItems().clear();
                                try {
                                    for (TreeMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
                                        Set set = interFaceDetail.entrySet();
                                        Iterator interFaceHashDetailIterator = set.iterator();
                                        while (interFaceHashDetailIterator.hasNext()) {
                                            Map.Entry me = (Map.Entry) interFaceHashDetailIterator.next();
                                            String[] deviceNameAndiniterFaceValue = me.getValue().toString().split("\\_");
                                            if (deviceNameAndiniterFaceValue[1].equals(topologyLink.destDevicesInTopoEditor.getSelectionModel().getSelectedItem())) {
                                                if (!me.getKey().toString().equals("")) {
                                                    topologyLink.interfaceList4.getItems().add(me.getKey().toString());
                                                }
                                            }
                                        }
                                    }
                                } catch (Exception e) {
                                }
                            }
                        });
                        topologyLink.finishSelectedLink.setOnAction(new EventHandler<ActionEvent>() {

                            @Override
                            public void handle(ActionEvent arg0) {                    
                                connect.setId(topologyLink.nameText.getText() + "_" + connecting.getStartX() + "_" + connecting.getStartY() + "_" + connecting.getEndX() + "_" + connecting.getEndY());
                                String detailedString = topologyLink.nameText.getText() + "_" + topologyLink.typeText.getText() + "_" + topologyLink.devicesInTopoEditor.getSelectionModel().getSelectedItem() + "_" + topologyLink.interfaceList2.getSelectionModel().getSelectedItem() + "_" + topologyLink.destDevicesInTopoEditor.getSelectionModel().getSelectedItem() + "_" + topologyLink.interfaceList4.getSelectionModel().getSelectedItem() + "_";
                                linkTopologyHash.put(connect.getId(), detailedString);
                                arrayOfLinkTopologyHash.add(linkTopologyHash);
                                topologyLink.copyStage.close();
                            }
                        });
                    } else if (arg0.getButton() == MouseButton.SECONDARY) {
                        deleteLineContextMenu(new DraggableNode(), connect, arg0);
                    }
                }
            });
            connect.setOnMouseEntered(new EventHandler<MouseEvent>() {

                @Override
                public void handle(MouseEvent arg0) {
                    connect.setStroke(Color.GOLD);
                    anchor1.setVisible(true);
                    anchor2.setVisible(true);

                }
            });
            connect.setOnMouseExited(new EventHandler<MouseEvent>() {

                @Override
                public void handle(MouseEvent arg0) {
    
                    connect.setStroke(Color.MIDNIGHTBLUE);
                    anchor1.setVisible(false);
                    anchor2.setVisible(false);

                }
            });
            hPane.getChildren().add(connect);
        }
        }
        

    }

    void insertImage1(Image i, Tab hb) {

        ImageView iv = new ImageView();
        iv.setImage(i);

        setupGestureSource(iv);
    }

    void setupGestureTarget(final HBox targetBox) {

        targetBox.setOnDragOver(new EventHandler<DragEvent>() {

            @Override
            public void handle(DragEvent event) {

                Dragboard db = event.getDragboard();

                if (db.hasImage()) {
                    event.acceptTransferModes(TransferMode.COPY);
                }

                event.consume();
            }
        });

        targetBox.setOnDragDropped(new EventHandler<DragEvent>() {

            @Override
            public void handle(DragEvent event) {

                Dragboard db = event.getDragboard();

                if (db.hasImage()) {

//                    insertImage(db.getImage(), targetBox);

                    event.setDropCompleted(true);
                } else {
                    event.setDropCompleted(false);
                }

                event.consume();
            }
        });

    }

    void setupGestureSource(final ImageView source) {

        source.setOnDragDetected(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent event) {

                /*
                 * allow any transfer mode
                 */
                Dragboard db = source.startDragAndDrop(TransferMode.COPY);

                /*
                 * put a image on dragboard
                 */
                ClipboardContent content = new ClipboardContent();

                Image sourceImage = source.getImage();
                content.putImage(sourceImage);
                db.setContent(content);

                event.consume();
            }
        });

    }

    void deleteLineContextMenu(final DraggableNode contentLine, final Line connecting, MouseEvent arg0) {

        ContextMenu menu = new ContextMenu();
        MenuItem item = new MenuItem("Delete Line");
       item.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent arg0) {
                contentLine.setVisible(false);
                contentLine.getChildren().remove(connecting);
            }
        });

        menu.getItems().add(item);
        menu.show(contentLine, arg0.getScreenX(), arg0.getScreenY());

    }

    public ArrayList<TextField> getDeviceNameList() {
        return deviceNameList;
    }

    
    public void closeActionForAnchorsRemoval(final Button closeButton, final VBox hbox, final ArrayList<Node> removeNodes,final DraggableNode content) {
        
     closeButton.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent arg0) {


                Node parent = hbox.getParent();
                Pane hb = (Pane) canvasTab.getContent();
                ObservableList<Node> allCurrentNode = hb.getChildren();

                for (Node node : allCurrentNode) {
                    if (node.toString().contains("Line")) {
                        if (!node.toString().matches("Line[id=Line[id=null,null]]")) {
                            if (node.getId() != null) {
                                String[] startLineNode = node.getId().split(",");
                                Integer nodeHash = content.hashCode();
                                if (nodeHash.toString().equals(startLineNode[0])) {
                                   
                                    removeNodes.add(node);
                                }
                                if (startLineNode.length == 2) {
                                    if (nodeHash.toString().equals(startLineNode[1])) {
                                        try {
                                            removeNodes.add(node);
                                        } catch (Exception e) {
                                        }
                                        

                                    }
                                }
                            }

                        }
                    }
                }
             if (!removeNodes.isEmpty()){
                for (Node removenode : removeNodes) {
                    try {
                        hb.getChildren().remove(removenode);
                    } catch (Exception e) {
                    }              
                }
             }
                hb.getChildren().remove(content);

            }
        });
}
      
    public void writeInFile(String path, String demoFile) {
        try {
            // Create file 
            FileWriter fstream = new FileWriter(path);
            BufferedWriter out = new BufferedWriter(fstream);
            out.write(demoFile);
            //Close the output stream
            out.close();
        } catch (Exception e) {//Catch exception if any
     
        }
    }

    private void enableNodeDrag(final DraggableNode node) {
        final TopologyNode.Delta dragDelta = new TopologyNode.Delta();
        node.setOnMousePressed(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
               dragDelta.x = node.getLayoutX() - mouseEvent.getX();
                dragDelta.y = node.getLayoutY() - mouseEvent.getY();
                node.getScene().setCursor(Cursor.MOVE);
            }
        });
        node.setOnMouseReleased(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
                node.getScene().setCursor(Cursor.HAND);
            }
        });
        node.setOnMouseDragged(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
                node.setLayoutX(mouseEvent.getX() + dragDelta.x);
                node.setLayoutY(mouseEvent.getY() + dragDelta.y);
            }
        });
        node.setOnMouseEntered(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
                if (!mouseEvent.isPrimaryButtonDown()) {
                    node.getScene().setCursor(Cursor.HAND);
                }
            }
        });
        node.setOnMouseExited(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
                if (!mouseEvent.isPrimaryButtonDown()) {
                    node.getScene().setCursor(Cursor.DEFAULT);
                }
            }
        });
    }

    private void testIntersections() {
        intersections.clear();

       for (Node src : nodesPresent) {
            for (Node dest : nodesPresent) {

                TopologyNode.ShapePair pair = new TopologyNode.ShapePair(src, dest);
                if ((!(pair.a instanceof DraggableNode) && !(pair.b instanceof DraggableNode))
                        && !intersections.contains(pair)
                        && pair.intersects(selectedBoundsType.get())) {
                    intersections.add(pair);
                }
            }
        }
    }

    private void enableDragLineWithAnchors(final Line connecting, final Circle anchor1, final Circle anchor2) {
        final Delta dragDelta = new Delta();

        connecting.setOnMousePressed(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
               dragDelta.x = connecting.getLayoutX() - mouseEvent.getX();
                dragDelta.y = connecting.getLayoutY() - mouseEvent.getY();
                dragDelta.x = anchor1.getLayoutX() - mouseEvent.getX();
                dragDelta.y = anchor1.getLayoutY() - mouseEvent.getY();
                dragDelta.x = anchor2.getLayoutX() - mouseEvent.getX();
                dragDelta.y = anchor2.getLayoutY() - mouseEvent.getY();
                connecting.getScene().setCursor(Cursor.MOVE);
            }
        });
        connecting.setOnMouseReleased(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
                connecting.getScene().setCursor(Cursor.HAND);
            }
        });
        connecting.setOnMouseDragged(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
                connecting.setLayoutX(mouseEvent.getX() + dragDelta.x);
                connecting.setLayoutY(mouseEvent.getY() + dragDelta.y);
                anchor1.setLayoutX(mouseEvent.getX() + dragDelta.x);
                anchor1.setLayoutY(mouseEvent.getY() + dragDelta.y);
                anchor2.setLayoutX(mouseEvent.getX() + dragDelta.x);
                anchor2.setLayoutY(mouseEvent.getY() + dragDelta.y);

            }
        });
        connecting.setOnMouseEntered(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
                if (!mouseEvent.isPrimaryButtonDown()) {
                    connecting.getScene().setCursor(Cursor.HAND);
                }
            }
        });
        connecting.setOnMouseExited(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
                if (!mouseEvent.isPrimaryButtonDown()) {
                    connecting.getScene().setCursor(Cursor.DEFAULT);
                }
            }
        });
    }

    private void enableDrag(final Circle circle) {
        final TopologyNode.Delta dragDelta = new TopologyNode.Delta();
        circle.setOnMousePressed(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
                // record a delta distance for the drag and drop operation.
                dragDelta.x = circle.getCenterX() - mouseEvent.getX();
                dragDelta.y = circle.getCenterY() - mouseEvent.getY();
                circle.getScene().setCursor(Cursor.MOVE);
            }
        });
        circle.setOnMouseReleased(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
            }
        });
        circle.setOnMouseDragged(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
                circle.setCenterX(mouseEvent.getX() + dragDelta.x);
                circle.setCenterY(mouseEvent.getY() + dragDelta.y);
            }
        });
        circle.setOnMouseEntered(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
                if (!mouseEvent.isPrimaryButtonDown()) {
                    circle.getScene().setCursor(Cursor.HAND);
                }
            }
        });
        circle.setOnMouseExited(new EventHandler<MouseEvent>() {

            @Override
            public void handle(MouseEvent mouseEvent) {
                if (!mouseEvent.isPrimaryButtonDown()) {
                }
            }
        });
    }

    class Anchor extends Circle {

        Anchor(String id, DoubleProperty x, DoubleProperty y) {
            super(x.get(), y.get(), 7);
            setId(id);
            setFill(Color.ANTIQUEWHITE.deriveColor(1, 1, 1, 0.75));
            setStroke(Color.GREY);
            x.bind(centerXProperty());
            y.bind(centerYProperty());
        }
    }

    class Anchor2 extends DraggableNode {

        Anchor2(String id, DoubleProperty x, DoubleProperty y) {
            super();
            setId(id);
            x.bind(layoutXProperty());
            y.bind(layoutYProperty());
        }
    }

    class Delta {

        double x, y;
    }

    class ShapePair {

        private Node a, b;

        public ShapePair(Node src, Node dest) {
            this.a = src;
            this.b = dest;
        }

        public boolean intersects(TopologyNode.BoundsType boundsType) {
            if (a == b) {
                return false;
            }

            a.intersects(b.getBoundsInLocal());
            switch (boundsType) {
                case LAYOUT_BOUNDS:
                    return a.getLayoutBounds().intersects(b.getLayoutBounds());
                case BOUNDS_IN_LOCAL:
                    return a.getBoundsInLocal().intersects(b.getBoundsInLocal());
                case BOUNDS_IN_PARENT:
                    return a.getBoundsInParent().intersects(b.getBoundsInParent());
                default:
                    return false;
            }
        }

        @Override
        public String toString() {
            return a.getId() + " : " + b.getId();
        }

        @Override
        public boolean equals(Object other) {
            TopologyNode.ShapePair o = (TopologyNode.ShapePair) other;
            return o != null && ((a == o.a && b == o.b) || (a == o.b) && (b == o.a));
        }

        @Override
        public int hashCode() {
            int result = a != null ? a.hashCode() : 0;
            result = 31 * result + (b != null ? b.hashCode() : 0);
            return result;
        }
    }
}
