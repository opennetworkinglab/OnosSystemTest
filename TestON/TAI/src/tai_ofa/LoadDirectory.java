/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import java.io.File;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.BasicFileAttributes;
import javafx.event.Event;
import javafx.event.EventHandler;
import javafx.scene.Node;
import javafx.scene.control.TreeItem;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;

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
public class LoadDirectory extends TreeItem<String> {

    //this stores the full path to the file or directory
    OFAFileOperations fileOperation = new OFAFileOperations();
    private String fullPath;

    public String getFullPath() {
        return (this.fullPath);
    }
    private boolean isDirectory;

    public boolean isDirectory() {
        return (this.isDirectory);
    }

    public LoadDirectory(Path file) {
        super(file.toString());
        this.fullPath = file.toString();

        if (Files.isDirectory(file)) {
            this.isDirectory = true;

            if ("common".equals(file.getFileName().toString())) {
                Node rootIcon = new ImageView(new Image(getClass().getResourceAsStream("/images/project.jpeg"), 20, 20, true, true));
                rootIcon.setId("/images/project.jpeg");
                this.setGraphic(rootIcon);
            } else if ("cli".equalsIgnoreCase(file.getFileName().toString())) {
                Node rootIcon2 = new ImageView(new Image(getClass().getResourceAsStream("/images/terminal.png"), 20, 20, true, true));
                rootIcon2.setId("/images/terminal.png");
                this.setGraphic(rootIcon2);
            } else if ("api".equals(file.getFileName().toString())) {
                Node rootIcon3 = new ImageView(new Image(getClass().getResourceAsStream("/images/api.jpg"), 20, 20, true, true));
                rootIcon3.setId("/images/api.jpg");
                this.setGraphic(rootIcon3);
            } else if ("tool".equals(file.getFileName().toString())) {
                Node rootIcon4 = new ImageView(new Image(getClass().getResourceAsStream("/images/tool.jpg"), 20, 20, true, true));
                this.setGraphic(rootIcon4);
            } else if ("remotesys".equals(file.getFileName().toString())) {
                Node rootIcon5 = new ImageView(new Image(getClass().getResourceAsStream("/images/automatorui.png"), 20, 20, true, true));
                this.setGraphic(rootIcon5);
            } else if ("emulator".equals(file.getFileName().toString())) {
                Node rootIcon6 = new ImageView(new Image(getClass().getResourceAsStream("/images/emulator.jpg"), 20, 20, true, true));
                this.setGraphic(rootIcon6);
            } else if ("controller".equals(file.getFileName().toString())) {
                Node rootIcon6 = new ImageView(new Image(getClass().getResourceAsStream("/images/controller.jpg"), 20, 20, true, true));
                this.setGraphic(rootIcon6);
            } else if ("remotetestbed".equals(file.getFileName().toString())) {
                Node rootIcon5 = new ImageView(new Image(getClass().getResourceAsStream("/images/testbed.jpg"), 20, 20, true, true));
                this.setGraphic(rootIcon5);
            }

        } else {
            this.isDirectory = false;
            String fileName = file.getFileName().toString();
            String ext = fileOperation.getExtension(fileName);
            if (".py".equals(ext)) {
                if ("fvtapidriver.py".equalsIgnoreCase(fileName)) {
                    Node rootIcon7 = new ImageView(new Image(getClass().getResourceAsStream("/images/flowvisor.png"), 20, 20, true, true));
                    rootIcon7.setId("/images/flowvisor.png");
                    this.setGraphic(rootIcon7);
                } else if ("mininetclidriver.py".equalsIgnoreCase(fileName)) {
                    Node rootIcon8 = new ImageView(new Image(getClass().getResourceAsStream("/images/mininet.jpg"), 20, 20, true, true));
                    rootIcon8.setId("/images/mininet.jpg");
                    this.setGraphic(rootIcon8);
                } else if ("poxclidriver.py".equalsIgnoreCase(fileName)) {
                    Node rootIcon9 = new ImageView(new Image(getClass().getResourceAsStream("/images/pox.jpg"), 20, 20, true, true));
                    rootIcon9.setId("/images/pox.jpg");
                    this.setGraphic(rootIcon9);
                } else if ("dpctlclidriver.py".equals(fileName)) {
                    Node rootIcon10 = new ImageView(new Image(getClass().getResourceAsStream("/images/dpctl.jpg"), 20, 20, true, true));
                    rootIcon10.setId("/images/dpctl.jpg");
                    this.setGraphic(rootIcon10);
                } else if ("hpswitchclidriver.py".equalsIgnoreCase(fileName)) {
                    Node rootIcon11 = new ImageView(new Image(getClass().getResourceAsStream("/images/hp.jpg"), 20, 20, true, true));
                    rootIcon11.setId("/images/hp.jpg");
                    this.setGraphic(rootIcon11);
                } else if ("cisco.py".equalsIgnoreCase(fileName)) {
                    Node rootIcon12 = new ImageView(new Image(getClass().getResourceAsStream("/images/Cisco.png"), 20, 20, true, true));
                    rootIcon12.setId("/images/Cisco.png");
                    this.setGraphic(rootIcon12);
                } else if ("flowvisorclidriver.py".equalsIgnoreCase(fileName)) {
                    Node rootIcon12 = new ImageView(new Image(getClass().getResourceAsStream("/images/flowvisor.png"), 20, 20, true, true));
                    rootIcon12.setId("/images/flowvisor.png");
                    this.setGraphic(rootIcon12);
                } else if ("floodlightclidriver.py".equalsIgnoreCase(fileName)) {
                    Node rootIcon11 = new ImageView(new Image(getClass().getResourceAsStream("/images/floodlight.jpg"), 20, 20, true, true));
                    rootIcon11.setId("/images/floodlight.jpg");
                    this.setGraphic(rootIcon11);
                } else if ("remotevmdriver.py".equalsIgnoreCase(fileName)) {
                    Node rootIcon11 = new ImageView(new Image(getClass().getResourceAsStream("/images/remotevm.jpg"), 20, 20, true, true));
                    rootIcon11.setId("/images/remotevm.jpg");
                    this.setGraphic(rootIcon11);
                } else if ("remotepoxdriver.py".equalsIgnoreCase(fileName)) {
                    Node rootIcon11 = new ImageView(new Image(getClass().getResourceAsStream("/images/pox.jpg"), 20, 20, true, true));
                    rootIcon11.setId("/images/pox.jpg");
                    this.setGraphic(rootIcon11);
                } else if ("flowvisordriver.py".equalsIgnoreCase(fileName)) {
                    Node rootIcon11 = new ImageView(new Image(getClass().getResourceAsStream("/images/flowvisor.png"), 20, 20, true, true));
                    rootIcon11.setId("/images/flowvisor.png");
                    this.setGraphic(rootIcon11);
                } else if ("switchclidriver.py".equalsIgnoreCase(fileName)) {
                    Node rootIcon11 = new ImageView(new Image(getClass().getResourceAsStream("/images/switchVM.png"), 20, 20, true, true));
                    rootIcon11.setId("/images/switchVM.png");
                    this.setGraphic(rootIcon11);
                } else {
                    Node rootIcon6 = new ImageView(new Image(getClass().getResourceAsStream("/images/defaultTerminal.png"), 20, 20, true, true));
                    rootIcon6.setId("/images/defaultTerminal.png");
                    this.setGraphic(rootIcon6);
                }
            }
            //if you want different icons for different file types this is where you'd do it
        }
        if (!fullPath.endsWith(File.separator)) {
            String finalValue = null;
            String value = file.getFileName().toString();
            String ext = fileOperation.getExtension(value);
            if (ext == null) {
                this.setValue(value);
            } else {
                if (ext.equals(".py")) {
                    finalValue = value.replace(ext, "");
                }
                this.setValue(finalValue);
            }

        }
        this.addEventHandler(TreeItem.branchExpandedEvent(), new EventHandler() {
            @Override
            public void handle(Event e) {
                LoadDirectory source = (LoadDirectory) e.getSource();
                if (source.isDirectory() && source.isExpanded()) {
                }
                try {
                    if (source.getChildren().isEmpty()) {
                        Path path = Paths.get(source.getFullPath());
                        BasicFileAttributes attribs = Files.readAttributes(path, BasicFileAttributes.class);
                        if (attribs.isDirectory()) {
                            DirectoryStream<Path> dir = Files.newDirectoryStream(path);
                            for (Path file : dir) {
                                LoadDirectory treeNode = new LoadDirectory(file);
                                if (treeNode.getValue() != null && !treeNode.getValue().equals("__init__") && !treeNode.getValue().equals("controllerdriver") && !treeNode.getValue().equals("apidriver")
                                        && !treeNode.getValue().equals("clidriver") && !treeNode.getValue().equals("controllerdriver") && !treeNode.getValue().equals("emulatordriver") && !treeNode.getValue().equals("toolsdriver") && !treeNode.getValue().equals("remotesysdriver")) //source.getChildren().add(treeNode);
                                {
                                    source.getChildren().add(treeNode);
                                }
                                treeNode.setExpanded(true);
                            }
                        }
                    }

                } catch (Exception ex) {
                }
            }
        });
        this.addEventHandler(TreeItem.branchCollapsedEvent(), new EventHandler() {
            @Override
            public void handle(Event e) {
                LoadDirectory source = (LoadDirectory) e.getSource();
                if (source.isDirectory() && !source.isExpanded()) {
                    ImageView iv = (ImageView) source.getGraphic();
                }
            }
        });


    }
}
