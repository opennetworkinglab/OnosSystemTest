#! /usr/bin/python

from __future__ import print_function
from datetime import date, datetime, timedelta
import mysql.connector
import random
import sys
import argparse

host_ip = "10.128.5.54"
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Specify test name")
parser.add_argument("-minimum", "--minimum",type=float, help="Minimum value of test")
parser.add_argument("-maximum", "--maximum",type=float, help="Maximum value of test")
parser.add_argument("-average", "--average",type=float, help="Average value of test")
args = parser.parse_args()

cnx = mysql.connector.connect(user='root', password='onos_test', host=host_ip, database='ONOS_Perf', port=3306)
cursor = cnx.cursor()

today = datetime.now()
tomorrow = datetime.now().date() + timedelta(days=1)
data_min = args.minimum 
data_max = args.maximum
data_avg = args.average
testName = args.name

add_results = ("INSERT INTO onos_perf ""(testName, date, min, avg, max) ""VALUES (%(testName)s, %(date)s, %(min)s, %(avg)s, %(max)s)")

data_results1 = {
                'testName' : str(testName),
                'date' : today,
                'min' : '%04.3f' % float(data_min),
                'max' : '%04.3f' % float(data_max),
                'avg' : '%04.3f' % float(data_avg),
                }

cursor.execute(add_results, data_results1)
today = today + timedelta(days=1)
#Make sure data is committed to the database#
cnx.commit()

cursor.close()
cnx.close()
