/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import javafx.beans.property.DoubleProperty;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.scene.Cursor;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.input.MouseButton;
import javafx.scene.input.MouseDragEvent;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.Pane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Line;
import javafx.scene.shape.StrokeLineCap;
import javafx.stage.Stage;

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
class OFAAnchorInsideImageNode {

    Double increaseBindX;
    Double increaseBindY;
    /*Double addX and addY is passed as an argument as binding coordinates are different for Wizard
     and toplogyNode(In the editor)*/

    public OFAAnchorInsideImageNode(Double addX, Double addY) {
        increaseBindX = addX;
        increaseBindY = addY;
    }
    boolean anchorFlag = false;
    OFATopologyLink topologyLink = new OFATopologyLink();
    ArrayList<HashMap<String, String>> arrayOfLinkTopologyHash = new ArrayList<HashMap<String, String>>();

    public void anchorsInsideImage(final TopologyWizard.Anchor anchor, final double bindLineStartx, final double bindLineStarty, final double bindLineEndx, final double bindLineEndy, final Pane hb, final DraggableNode content,
            final VBox hbox, final Line con, final ArrayList<String> draggedImagesName, final ArrayList<HashMap<String, String>> arrayOfInterFaceHash, final HashMap<String, String> linkTopologyHash, final HashMap<Node, String> anchorNodeHash) {
        final Line con11 = new Line();

        anchor.setOnDragDetected(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent arg0) {
                anchor.startFullDrag();
                enableDrag(anchor);
            }
        });

        anchor.setOnMouseDragReleased(new EventHandler<MouseDragEvent>() {
            @Override
            public void handle(MouseDragEvent arg0) {
                ObservableList<Node> allNodesCanvas = hb.getChildren();
                boolean flag = false;
                String startNode = null;
                String endNode = null;
                try {
                    for (Node node : allNodesCanvas) {
                        Double x = node.getLayoutX() + increaseBindX;
                        Double y = node.getLayoutY() + increaseBindY;
                        if (node.toString().startsWith("DraggableNode")) {
                            for (int i = 0; i <= 80; i++) {
                                for (int j = 0; j <= 100; j++) {
                                    Double x1 = node.getLayoutX() + increaseBindX;
                                    Double y1 = node.getLayoutY() + increaseBindY;
                                    Double x11 = x1 + i;
                                    Double y11 = y1 + j;
                                    if (x11 == arg0.getSceneX()) {
                                        if (y11 == arg0.getSceneY()) {
                                            con11.setStrokeLineCap(StrokeLineCap.ROUND);
                                            con11.setStroke(Color.MIDNIGHTBLUE);
                                            con11.setStrokeWidth(2.0);
                                            con11.startXProperty().bind(content.layoutXProperty().add(bindLineStartx));
                                            con11.startYProperty().bind(content.layoutYProperty().add(bindLineStarty));
                                            startNode = ((Integer) content.hashCode()).toString();
                                            con11.endXProperty().bind(node.layoutXProperty().add(bindLineEndx));
                                            con11.endYProperty().bind(node.layoutYProperty().add(bindLineEndy));
                                            endNode = ((Integer) node.hashCode()).toString();
                                            con11.setId(startNode + "," + endNode);
                                            hbox.setStyle("-fx-border-color: Transparent");
                                            con.setVisible(false);
                                            anchor.setVisible(false);
                                            hb.getChildren().add(con11);
                                            flag = true;

                                            Map<Node, String> map = anchorNodeHash;
                                            Iterator<Map.Entry<Node, String>> entries = map.entrySet().iterator();
                                            while (entries.hasNext()) {
                                                Map.Entry<Node, String> entry = entries.next();
                                                entry.getKey();
                                                hb.getChildren().remove(entry.getKey());
                                            }
                                        }
                                    }
                                }
                            }

                        }


                    }
                    if (flag == false) {
                        Map<Node, String> map = anchorNodeHash;
                        Iterator<Map.Entry<Node, String>> entries = map.entrySet().iterator();
                        while (entries.hasNext()) {
                            Map.Entry<Node, String> entry = entries.next();
                            entry.getKey();
                            hb.getChildren().remove(entry.getKey());
                            anchorFlag = false;
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
                    if (arrayOfLinkTopologyHash.isEmpty()) {
                        for (HashMap<String, String> linkHash : arrayOfLinkTopologyHash) {
                            Set linkSet = linkHash.entrySet();
                            Iterator linkHashDetailIterator = linkSet.iterator();
                            while (linkHashDetailIterator.hasNext()) {

                                Map.Entry linkMap = (Map.Entry) linkHashDetailIterator.next();
                                if (linkMap.getKey().toString().equals(con11.getId())) {
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

                    for (String string : draggedImagesName) {
                        topologyLink.devicesInTopoEditor.getItems().add(string);
                        topologyLink.destDevicesInTopoEditor.getItems().add(string);
                    }
                    topologyLink.devicesInTopoEditor.setOnAction(new EventHandler<ActionEvent>() {
                        @Override
                        public void handle(ActionEvent arg0) {
                            topologyLink.interfaceList2.getItems().clear();
                            try {
                                for (HashMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
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
                                for (HashMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
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
                            arrayOfLinkTopologyHash = new ArrayList<HashMap<String, String>>();
                            arrayOfLinkTopologyHash.add(linkTopologyHash);
                            topologyLink.copyStage.close();
                        }
                    });
                } else if (arg0.getButton() == MouseButton.SECONDARY) {
                }
            }
        });
    }

    public void closeNodeOnCanvas(final Button closeButton, final VBox hbox, final Pane hb, final DraggableNode content) {
        final ArrayList<Node> removeNodes = new ArrayList<Node>();

        closeButton.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent arg0) {
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
            }
        });
    }

    private void enableDrag(final Circle circle) {
        final OFAAnchorInsideImageNode.Delta dragDelta = new OFAAnchorInsideImageNode.Delta();

        circle.setOnMousePressed(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent mouseEvent) {
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

    class Delta {

        double x, y;
    }
}
