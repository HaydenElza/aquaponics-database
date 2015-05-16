# Hayden Elza
# hayden.elza@gmail.com
# version 0.1  05-15-15
# python version 3.4.3


import postgresql
import sys




db = postgresql.open("pq://postgres:postgres@localhost/aqua")  # Open database


for row in db.prepare("select * from public.address;"):
	print (row)