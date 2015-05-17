import postgresql
import csv
import time, datetime
from datetime import date
import os.path
import locale
locale.setlocale( locale.LC_ALL, '' )


def order_details(num1,num2,num3):
	print (num1)
	print (num2)
	print (num3)


def place_order(order_id, cust_id, amount, delivery_status, order_date, delivery_date, notes, order_details):
	att = ['324898162', '034623913', '35.00', "0", '03/15/2015', '03/16/2015', "NULL"]
	att = [str(i) for i in att]
	for i in [4,5]: att[i] = date(int(att[i].split("/")[2]),int(att[i].split("/")[0]),int(att[i].split("/")[1]))
	print (att[4],att[5])

place_order('324898162', '034623913', '35.00', "0", '03/15/2015', '03/16/2015', "NULL", [['apple', '5'],['pear', '2']])