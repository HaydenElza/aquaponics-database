import postgresql
import csv
import time, datetime
from datetime import date
import os.path
import locale
locale.setlocale( locale.LC_ALL, '' )


att = ['apple', '10', '5.00']
print (locale.currency(float(att[2])))