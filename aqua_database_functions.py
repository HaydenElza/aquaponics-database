# Hayden Elza
# hayden.elza@gmail.com
# version 0.1  05-15-15
# python version 3.4.3


import postgresql
import csv
import time, datetime
import os.path


db = postgresql.open("pq://postgres:postgres@localhost/aqua")  # Open database


def print_orders():
	out_path = "/home/babykitty/Orders_" + datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d") + ".csv"
	if os.path.isfile(out_path):
		print (out_path, "already exists, aborting. If you would like to make a new Orders CSV, move or delete the pre-existing CSV for today's date.")
		return

	# Set ouput csv file
	fout = open(out_path,"a")


	for row in db.prepare('select c.fname, c.lname, od.food_item, od.quantity from order_details od join "order" o on o.order_id = od.order_id join customer c on o.cust_id = c.cust_id ORDER BY fname asc, lname asc, food_item asc;'):
		for column in row:
			item = str(column) + ","
			fout.write(item)
		fout.write("\n")

	print ("Orders exported to", out_path)
	fout.close()

def add_customer():

def add_record():

def add_to_inventory():

def remove_from_inventory():

def place_order():

def delivery_sequence():




print_orders()