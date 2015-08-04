import inspect
import sys
import os
import re
from core import xmldict
'''
@author: Raghav Kashyap (raghavkashyap@paxterrasolutions.com)

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.


'''


class UpdateDriver:
    def __init__(self):
        self.default = ''
        self.configFile = "/home/openflow/TestON/config/ofadriver.cfg"
        self.methodDict = {}
        self.fileDict = {}


    def getmethods(self,modulePath,Class) :
        '''
         This will get the list of methods in given module or class.
         It accepts the module path and class name. If there is no
         class name then it has be mentioned as None.
        '''
        methodList = []
        moduleList = modulePath.split("/")
        newModule = ".".join([moduleList[len(moduleList) - 2],moduleList[len(moduleList) - 1]])
        print "Message : Method list is being obatined , Please wait ..."
        try :
            if Class :
                Module = __import__(moduleList[len(moduleList) - 1], globals(), locals(), [Class], -1)
                ClassList = [x.__name__ for x in Module.__dict__.values() if inspect.isclass(x)]
                self.ClassList = ClassList
                Class = vars(Module)[Class]
                methodList = [x.__name__ for x in Class.__dict__.values() if inspect.isfunction(x)]
            else :
                Module = __import__(moduleList[len(moduleList) - 1], globals(), locals(),[moduleList[len(moduleList) - 2]], -1)
                methodList = [x.__name__ for x in Module.__dict__.values() if inspect.isfunction(x)]
                ClassList = [x.__name__ for x in Module.__dict__.values() if inspect.isclass(x)]
                self.ClassList = ClassList
        except :
            print "Error : " +str(sys.exc_info()[1])


        self.method = methodList
        return self.method

    def echo(self) :
        print "Echoing !!!!!!"

    def getargs(self,moduleName,className,method) :
        '''
          This will return the list of arguments in a method of python module of class.
          It accepts method list as an argument.
        '''
        print "Message : Argument list is being obtained for each method"
        methodArgsDict = {}
        if className == None:
            moduleList = moduleName.split(".")
            for index,name in enumerate(method) :
                Module = __import__(moduleList[len(moduleList) -1], globals(), locals(), [moduleList[len(moduleList) -2]], -1)
                try :
                    names = vars(Module)[name]
                except KeyError:
                    print "Message : method '" + name + "'does not exists,Continued with including it. "
                    return False
                argumentList = inspect.getargspec(names) #inspect.getargvalues(name)
                methodArgsDict[name] = argumentList[0]
        else :
            moduleList = moduleName.split(".")
            for index,name in enumerate(method) :
                Module = __import__(moduleList[len(moduleList) - 1], globals(), locals(), [className], -1)
                Class = getattr(Module, className)
                try :
                    names = vars(Class)[name]
                except KeyError :
                    print "Message : method '" + name + "'does not exists,Continued with include it."
                    return False

                argumentList = inspect.getargspec(names) #inspect.getargvalues(name)
                methodArgsDict[name] = argumentList[0]

        return methodArgsDict

    def configparser(self,fileName):
        '''
         It will parse the config file (ofa.cfg) and return as dictionary
        '''

        matchFileName = re.match(r'(.*)\.cfg', fileName, re.M | re.I)
        if matchFileName:
            self.configFile = fileName
            try :
                xml = open(fileName).read()
                self.configDict = xmldict.xml_to_dict(xml)
                return self.configDict
            except :
                print "Error : Config file " + self.configFile + " not defined properly or file path error"


    def getList(self):
        '''
          This method will maintain the hash with module->class->methodList or
          module -> methodList .It will return the same Hash.
        '''
        classList = []
        try :
            moduleList = self.configDict['config-driver']['importTypes'][self.driver]['modules'].keys()
        except KeyError,e:
            print "Error : Module Does not Exists"
            print e
            return False

        for index,value in enumerate(moduleList):
            modulePath = self.configDict['config-driver']['importTypes'][self.driver]['modules'][value]['path']
            moduleName = self.configDict['config-driver']['importTypes'][self.driver]['modules'][value]['name']

            try :
                pathList = self.configDict['config-driver']['importTypes'][self.driver]['modules'][value]['set-path'].split(",")
                sys.path.extend(pathList)
            except KeyError :
                print "Error : No System Path is given "
                pass
            try :
                Class = self.configDict['config-driver']['importTypes'][self.driver]['modules'][value]['classes']
            except :
                Class = None
            if Class == None :
                methodList = self.getmethods(modulePath,None)
                self.methodDict[moduleName] =  methodList
                self.method_ignoreList(value,None)
                self.getMethodArgsHash(moduleName,value,None)
            else :
                classList = self.configDict['config-driver']['importTypes'][self.driver]['modules'][value]['classes'].keys()
                for indx,className in enumerate(classList):
                    if className == 'ignore-list' :
                        pass
                    else :
                        methodList = self.getmethods(modulePath,className)
                        self.methodDict[moduleName] = {className : methodList}
                        self.method_ignoreList(value,className)
                        self.class_ignoreList(value)
                        self.getMethodArgsHash(moduleName,value,className)

    def class_ignoreList(self,module) :
        '''
        It removes the ignored classes for each module mention in ofadriver.cfg
        '''
        class_ignoreList = []
        if self.configDict['config-driver']['importTypes'][self.driver]['modules'][module]['classes'] == None :
            pass
        else :
            try :
                class_ignoreList = str(self.configDict['config-driver']['importTypes'][self.driver]['modules'][module]['classes']['ignore-list']).split(",")
            except KeyError :
                print "Message : No Class Ignore List present"
                return True
        moduleName = self.configDict['config-driver']['importTypes'][self.driver]['modules'][module]['name']
        try :
            for index,className in enumerate(class_ignoreList):
                if className in self.methodDict[moduleName].keys():
                    del self.methodDict[moduleName][className]
        except AttributeError:
            pass
        return self.methodDict

    def method_ignoreList(self,module,className):
        '''
        It removes the ignored methods of each module or class mentioned in ofadriver.cfg.
        '''
        method_ignoreList = []

        try :
            if className == None :
                try :
                    method_ignoreList = str(self.configDict['config-driver']['importTypes'][self.driver]['modules'][module]['methods']['ignore-list']).split(",")
                except TypeError :
                    pass
            else :
                try :
                    method_ignoreList = str(self.configDict['config-driver']['importTypes'][self.driver]['modules'][module]['classes'][className]['methods']['ignore-list']).split(",")
                except TypeError :
                    pass
        except KeyError :
            print "Message : No Ignore-List Exists , proceeding for looking add method"
            self.add_method(module,className)
            return True

        moduleName = self.configDict['config-driver']['importTypes'][self.driver]['modules'][module]['name']
        #import pprint
        #pprint.pprint(self.methodDict[moduleName])
        for index, method in enumerate(method_ignoreList) :
            if className == None :
                try :
                    self.methodDict[moduleName].remove(method)
                    #pprint.pprint(self.methodDict)
                except ValueError:
                    print "Message : Method " + method + "Does not exist in module " + moduleName + ", Continue to rest execution"
                    pass

            else :
                if method in self.methodDict[moduleName][className] :
                    self.methodDict[moduleName][className].remove(method)
        self.add_method(module,className)
        return self.methodDict

    def add_method(self,module,className) :
        '''
         This  will add the methods(mentioned in ofadriver.cfg file) into method list if it doesnot exists in list.
        '''
        method_List = []
        try :
            if className == None :
                try :
                    method_List = str(self.configDict['config-driver']['importTypes'][self.driver]['modules'][module]['methods']['add-list']).split(",")
                except TypeError :
                    pass
            else :
                try :
                    method_List = str(self.configDict['config-driver']['importTypes'][self.driver]['modules'][module]['classes'][className]['methods']['add-list']).split(",")
                except TypeError :
                    pass

        except KeyError :
            print "Message : No Add-List Exists , Proceeding with all available methods"
            return True
        moduleName = self.configDict['config-driver']['importTypes'][self.driver]['modules'][module]['name']
        for index, method in enumerate(method_List) :
            if className == None :
                self.methodDict[moduleName] = []
                self.methodDict[moduleName].append(method)
            else :
                self.methodDict[moduleName][className] = []
                self.methodDict[moduleName][className].append(method)

    def getMethodArgsHash(self,moduleName,module,className):
        '''
         This will maintain a Hash of class->method->argumentsList
        '''
        modulePath = self.configDict['config-driver']['importTypes'][self.driver]['modules'][module]['path']
        moduleList = modulePath.split("/")
        newModule = ".".join([moduleList[len(moduleList) - 2],moduleList[len(moduleList) - 1]])
        if className == None :
            methodArgs = self.getargs(newModule,None,self.methodDict[moduleName])
            self.fileDict[moduleName] = methodArgs
        else :
            methodArgs = self.getargs(newModule,className,self.methodDict[moduleName][className])
            self.fileDict[className] = methodArgs
        return self.fileDict

    def appendDriver(self,fileName):
        '''
         This will append the given driver file with methods along with arguments.
        '''
        matchFileName = re.match(r'(.*)\.py', fileName, re.M | re.I)

        if matchFileName:
            fileHandle = None
            try :
                print "Message : Writing Driver file at " + fileName
                fileHandle = open(fileName,"a")
                content = ''

                for index, key in enumerate(self.fileDict.keys()):
                    try :
                        for ind, method in enumerate(self.fileDict[key].keys()):
                            if not method == "__init__" :
                                args = ''
                                args = ",".join(self.fileDict[key][method])
                                content = content + "\n" + " " * 4 + "def " + method + "(self," + args + ") :"
                                content = content + "\n" + " " * 8 + "return " + key + "." + method + "(" + args + ")\n"
                    except AttributeError :
                        pass
                fileHandle.write(content)
                fileHandle.close()
                return content

            except :
                print "Error : Driver file " + fileName + "does not exists"
        else :
             print "Error : File name " + fileName + "is not python module"
             return False


    def writeDriver(self, driver) :
        '''
         This will accept the List of driver name and write those drivers if no driver name is specified
         then it will write all of the driver specified in the ofadriver.cfg.
        '''
        self.printHeader(driver)
        drivers = []
        commaMatch  = re.search(",", driver, flags=0)
        if commaMatch:
            drivers = driver.split(",")
        else :
            drivers.append(driver)
        self.driverList = []
        if len(drivers) == 0:
            for index, driverName in enumerate(self.configDict['config-driver']['importTypes'].keys()):
                self.driver = driverName
                result = self.getList()
                if result :
                    self.getDriverPath()
                    self.appendDriver(self.driverPath + self.driver + ".py")
                    self.driverList.append(self.driverPath + self.driver + ".py")
                else :
                    return False
        else :
            for index, driverName in enumerate(drivers) :

                self.driver = driverName
                result = self.getList()
                if result :
                    self.getDriverPath()
                    self.appendDriver(self.driverPath + self.driver + ".py")
                    self.driverList.append(self.driverPath + self.driver + ".py")
                else :
                    return False

        print "=" * 90
        print " " * 30  + "Output Driver File :"
        print ",\n".join(self.driverList)
        print "=" * 90
        return True



    def getDriverPath(self):
        '''
         It will set the driver path and returns it.If driver path is not specified then it will take
         default path (/lib/updatedriver/).
        '''
        self.driverPath = ''
        try :
            self.driverPath = self.configDict['config-driver']['importTypes'][self.driver]['driver-path']

        except KeyError:
            location = os.path.abspath( os.path.dirname( __file__ ) )
            path = re.sub( "(bin)$", "", location )
            self.driverPath = path + "/lib/updatedriver/"
        return self.driverPath


    def printHeader(self,driver):
        content = ''

        print " " * 10 +"=" * 90 + "\n"
        content = content + " " * 30 + "*-- Welcome to Updated Driver --*\n"
        content = content + "\n" + " " * 10 + " " * 10 + "Config File : " + "/home/openflow/TestON/config/ofadriver.py"
        content = content + "\n" + " " * 10 + " " * 10 + "Drivers Name : " + driver
        print content
        print " " * 10 + "=" * 90



