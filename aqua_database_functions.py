# Hayden Elza
# hayden.elza@gmail.com
# version 0.1  05-15-15
# python version 3.4.3


import postgresql
import csv
import time, datetime
import os.path

# Modules of data type conversion
from datetime import date


db = postgresql.open("pq://postgres:postgres@localhost/aqua")  # Open database
x = db.xact()  # Used for transactions

def print_orders():
	out_path = "/home/babykitty/Orders_" + datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d") + ".csv"  # Set output path, date is added so that multiple order fulfillments may be placed in same directory.
	if os.path.isfile(out_path):
		print (out_path, "already exists, aborting. If you would like to make a new Orders CSV, move or delete the pre-existing CSV for today's date.")
		return

	fout = open(out_path,"a")  # Set ouput csv file

	for row in db.prepare('select c.fname, c.lname, od.food_item, od.quantity from order_details od join "order" o on o.order_id = od.order_id join customer c on o.cust_id = c.cust_id ORDER BY fname asc, lname asc, food_item asc;'):
		for column in row:
			item = str(column) + ","
			fout.write(item)
		fout.write("\n")

	print ("Orders exported to", out_path)
	fout.close()
	return

def add_customer(cust_id, fname, lname, phone_num, password, email, street, city, state, zip_code, country):
	x.start()  # Start transaction
	att = [cust_id, fname, lname, phone_num, password, email, street, city, state, zip_code, country]  # Create list of values for ease of use
	att = [str(i) for i in att]  # Make sure all elements in list are string
	try:  # Catch failed commands
		# First add the customer
		customer = db.prepare("insert into customer (cust_id, fname, lname, phone_num, password, email) VALUES ($1,$2,$3,$4,$5,$6);")
		customer(att[0], att[1],att[2],att[3],att[4],att[5])
		# Second add the customers address
		address = db.prepare("insert into address (cust_id, street, city, state, zip_code, country) VALUES ($1,$2,$3,$4,$5,$6);")
		address(att[0],att[6],att[7],att[8],att[9],att[10])
		x.commit()  # Commit successfull transaction
	except:
		print ("Transaction failed! Rolling back. Customer may already exist.")
		x.rollback()  # Rollback after failure
	return

def add_record(bed_num, date_planted, food_item, quantity, sell_by="NULL", date_harvested="NULL", mature_date="NULL", harvest_by="NULL", treatment="NULL", notes="NULL"):
	x.start()  # Start transaction
	att = [bed_num, date_planted, food_item, quantity, sell_by, date_harvested, mature_date, harvest_by, treatment, notes]  # Create list of values for ease of use
	att = [str(i) for i in att]  # Make sure all elements in list are string
	for i in [1,4,5,6,7]: att[i] = date(int(att[i].split("/")[2]),int(att[i].split("/")[0]),int(att[i].split("/")[1]))  # Disgusting date format fix
	try:  # Catch failed commands
		record = db.prepare("insert into planting_record (bed_num, date_planted, food_item, quantity, sell_by, date_harvested, mature_date, harvest_by, treatment, notes) VALUES ($1,cast($2 as date),$3,$4,$5,cast($6 as date),cast($7 as date),cast($8 as date),$9,$10);")
		record(att[0],att[1],att[2],att[3],att[4],att[5],att[6],att[7],att[8],att[9])
		x.commit()  # Commit successfull transaction
	except:
		print ("Transaction failed! Rolling back. Planting record may already exist, try editing. Hint: date format is dd/mm/yyyy and null vaules as 'NULL'")
		x.rollback()  # Rollback after failure
	return

def add_to_inventory(food_item, quantity, price):
	x.start()  # Start transaction
	att = [food_item, quantity, price]  # Create list of values for ease of use
	att = [str(i) for i in att]  # Make sure all elements in list are string
	try:  # Catch failed commands
		inventory = db.prepare("insert into inventory (food_item, quantity, price) VALUES ($1,$2,cast($3 as numeric));")
		inventory(att[0],att[1],att[2])
		x.commit()  # Commit successfull transaction
	except:
		print ("Transaction failed! Rolling back. Item may already be in inventory, try editing. Hint: price format example '5.00'")
		x.rollback()  # Rollback after failure
	return

def update_inventory(food_item, change):
	x.start()  # Start transaction
	att = [food_item, change]  # Create list of values for ease of use
	att[0] = str(att[0])  # Cast food_item as string
	att[1] = int(att[1])  # Cast change as integer

	# Check validity of change, i.e., not cause quantity to be less than 0
	check = db.prepare("select quantity from inventory where food_item=$1")
	quantity = check(att[0])[0][0]
	if quantity+att[1] < 0:
		print ("Transaction failed! You are trying to remove more items from inventory than exist.")
		x.rollback()  # Rollback after failure
		return

	try:  # Catch failed commands
		update = db.prepare("update inventory set quantity=(quantity+$2) where food_item=$1;")
		update(att[0],att[1])
		x.commit()  # Commit successfull transaction
	except:
		print ("Transaction failed! Rolling back. Item may not be in inventory.")
		x.rollback()  # Rollback after failure
	return

def order_details(order_id, food_item, quantity):
	att = [order_id, food_item, quantity]  # Create list of values for ease of use
	att = [str(i) for i in att]  # Make sure all elements in list are string
	details = db.prepare("""insert into order_details (order_id, food_item, quantity) VALUES ($1,$2,$3);""")
	details(att[0],att[1],att[2])

	# Update inventory, cannot call function because it will try to reopen transaction
	att = [food_item, quantity]  # Create list of values for ease of use
	att[0] = str(att[0])  # Cast food_item as string
	att[1] = int(att[1])  # Cast change as integer
	# Check validity of change, i.e., not cause quantity to be less than 0
	check = db.prepare("select quantity from inventory where food_item=$1")
	quantity = check(att[0])[0][0]
	if quantity+att[1] < 0:
		print ("Transaction failed! You are trying to remove more items from inventory than exist.")
		return
	try:  # Catch failed commands
		update = db.prepare("update inventory set quantity=(quantity+$2) where food_item=$1;")
		update(att[0],att[1])
	except:
		print ("Transaction failed! Rolling back. Item may not be in inventory.")

	return

def place_order(order_id, cust_id, amount, delivery_status, order_date, delivery_date, notes, items):
	x.start()  # Start transaction
	att = [order_id, cust_id, amount, delivery_status, order_date, delivery_date, notes]  # Create list of values for ease of use
	att = [str(i) for i in att]  # Make sure all elements in list are string
	for i in [4,5]: att[i] = date(int(att[i].split("/")[2]),int(att[i].split("/")[0]),int(att[i].split("/")[1]))  # Disgusting date format fix
	try:  # Catch failed commands
		# Insert into order
		order = db.prepare("""insert into "order" (order_id, cust_id, amount, delivery_status, date, delivery_date, notes) VALUES ($1,$2,cast($3 as numeric),$4,$5,$6,$7);""")
		order(att[0],att[1],att[2],att[3],att[4],att[5],att[6])
		# Insert into order_details
		for i in items:
			order_details(order_id,i[0],i[1])

		x.commit()  # Commit successfull transaction
	except:
		print ("Transaction failed! Rolling back. Item may not be in inventory or order may already exist. Hint: use format [[foo,bar],[foo,bar]] for order details")
		x.rollback()  # Rollback after failure
	return


def delivery_sequence():
	# Calculate variables
	date = '03/16/2015' #datetime.datetime.fromtimestamp(time.time()).strftime("%m/%d/%Y")
	sql = """select distinct seq, c.fname, c.lname, a.street, a.city, a.state, a.zip_code from (SELECT seq, id1, id2, round(cost::numeric, 2) AS cost FROM pgr_tsp($$select cast(cust_id as integer) as id, cast(ST_X(geom) as integer) as x, cast(ST_Y(geom) as integer) as y from (select distinct a.cust_id, a.geom from "order" o join address a on o.cust_id = a.cust_id where delivery_date='"""+date+"""' union select cust_id, geom from address where cust_id='000000000') as foo$$,cast('000000000' as integer))) as foo join address a on to_char(foo.id2,'fm000000000')=a.cust_id join customer c on c.cust_id=a.cust_id;"""
	
	# Export route to csv
	out_path = "/home/babykitty/Route_" + datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d") + ".csv"  # Set output path, date is added so that multiple order fulfillments may be placed in same directory.
	if os.path.isfile(out_path):
		print (out_path, "already exists, aborting. If you would like to make a new Route CSV, move or delete the pre-existing CSV for today's date.")
		return
	fout = open(out_path,"a")  # Set ouput csv file
	for row in db.prepare(sql):
		for column in row:
			item = str(column) + ","
			fout.write(item)
		fout.write("\n")
	print ("Orders exported to", out_path)
	fout.close()
	return
