#!/usr/bin/env python

import sys
import os
import re
import datetime
import time

#Create an html footer for inserting to wiki-markup.
#This script should be called after all tests have completed

output = ""

#jquery reference must be at the very bottom of the body to take effect
output += "<script type='text/javascript' src='http://ajax.googleapis.com/ajax/libs/jquery/1.3/jquery.min.js'></script>"
output += "</body>"
output += "</html>"
output += "{html}"

print output

