/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.util.ArrayList;

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
public class OFAFileOperations {

    BufferedReader input;
    ArrayList list = new ArrayList();
    ArrayList<String> filePath = new ArrayList<String>();

    public OFAFileOperations() {
    }

    public void writeInFile(String path, String demoFile) {
        try {
            FileWriter fstream = new FileWriter(path);
            BufferedWriter out = new BufferedWriter(fstream);
            out.write(demoFile);
            out.close();
        } catch (Exception e) {
        }
    }

    public String getContents(File aFile) {
        StringBuilder contents = new StringBuilder();

        try {
            //use buffering, reading one line at a time
            //FileReader always assumes default encoding is OK!
            try {
                input = new BufferedReader(new FileReader(aFile));
            } catch (Exception e) {
            }

            try {
                String line = null; //not declared within while loop

                while ((line = input.readLine()) != null) {
                    contents.append(line);
                    contents.append(System.getProperty("line.separator"));
                }
            } finally {
                try {
                    input.close();
                } catch (Exception e) {
                }

            }
        } catch (IOException ex) {
            ex.printStackTrace();
        }

        return contents.toString();
    }

    public String getExtension(String name) {
        String extension = null;
        try {

            if (name.contains(".")) {
                int dotPos = name.lastIndexOf(".");
                extension = name.substring(dotPos);
            }
        } catch (Exception e) {
        }

        return extension;
    }

    public String getFileName(String name) {
        String fileName = null;
        try {

            if (name.contains(".")) {
                int dotPos = name.lastIndexOf(".");
                fileName = name.substring(0, dotPos);
            }
        } catch (Exception e) {
        }

        return fileName;
    }

    public void setContents(File aFile, String aContents) throws FileNotFoundException, IOException {
        if (aFile == null) {
            throw new IllegalArgumentException("File should not be null.");
        }
        if (!aFile.exists()) {
            throw new FileNotFoundException("File does not exist: " + aFile);
        }
        if (!aFile.isFile()) {
            throw new IllegalArgumentException("Should not be a directory: " + aFile);
        }
        if (!aFile.canWrite()) {
            throw new IllegalArgumentException("File cannot be written: " + aFile);
        }

        //use buffering
        Writer output = new BufferedWriter(new FileWriter(aFile));
        try {
            //FileWriter always assumes default encoding is OK!
            output.write(aContents);
        } finally {
            output.close();
        }
    }

    public void saveFile(File saveToDisk, String content) throws FileNotFoundException, IOException {
        setContents(saveToDisk, content);
    }
    static int spc_count = -1;

    void Process(File aFile) {

        spc_count++;
        String spcs = "";
        for (int i = 0; i < spc_count; i++) {
            spcs += " ";
        }
        if (aFile.isFile()) {
            list.add(aFile.getName());
            filePath.add(aFile.getPath());

        } else if (aFile.isDirectory()) {
            File[] listOfFiles = aFile.listFiles();


            if (listOfFiles != null) {
                for (int i = 0; i < listOfFiles.length; i++) {
                    Process(listOfFiles[i]);
                }
            } else {
            }
        }
        spc_count--;

    }
}
