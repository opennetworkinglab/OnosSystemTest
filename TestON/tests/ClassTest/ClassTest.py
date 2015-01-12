
import time
import os
import re

class ClassTest:
    def __init__(self):
        self.default = ''

    def CASE1(self, main):
        import time
        import imp

        init = imp.load_source('ClassInit',
            '/home/admin/ONLabTest/TestON/tests/ClassTest/Dependency/ClassInit.py')

        ip1_from_class = init.getIp1()  
        init.printMain(main)

        main.log.info(ip1_from_class)

    def CASE2(self, main):


        main.log.info("Case 2")

