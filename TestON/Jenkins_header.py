#!/usr/bin/env python

import sys
import os
import re
import datetime
import time

#Create an html header for inserting to wiki-markup.
#This script should be called before posting the main body of the test results (Jenkins_getresult)

output = ""
#Start input to wiki markup. {html} tag is used in wiki markup to indicate a block of
#raw html format file. This can include scripts
output += "{html}"
output += "<!DOCTYPE html>"
output += "<html>"
output += "<body>"

print output
