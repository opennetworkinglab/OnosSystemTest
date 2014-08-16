#! /usr/bin/python

from __future__ import print_function
from datetime import date, datetime, timedelta
import mysql.connector
import random
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Specify test name")
parser.add_argument("-min", "--minimum",type=float, help="Minimum value of test")
parser.add_argument("-max", "--maximum",type=float, help="Maximum value of test")
parser.add_argument("-avg", "--average",type=float, help="Average value of test")
parser.add_argument("-host", "--host", default="10.128.5.54", help="Database host IP address. Default = 10.128.5.54")
parser.add_argument("-table", "--table", required=True, help="Tablename to insert in")
parser.add_argument("-db", "--database", default="ONOS_Perf", help="Database name to insert in. Default = ONOS_Perf")
args = parser.parse_args()

today = datetime.now()
tomorrow = datetime.now().date() + timedelta(days=1)
data_min = args.minimum
data_max = args.maximum
data_avg = args.average
testName = args.name
host_ip = args.host
db_name = args.database
table_name = args.table

cnx = mysql.connector.connect(user='root', password='onos_test', host=host_ip, database= str(db_name), port=3306)
cursor = cnx.cursor()

#NOTE: IMPORTANT - Ensure that you are inserting into the correct table. 
#This method may not be the most secure way to insert to database

add_results = ("INSERT INTO "+table_name+" ""(testName, date, min, avg, max) ""VALUES (%(testName)s, %(date)s, %(min)s, %(avg)s, %(max)s)")

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
