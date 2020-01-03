from datetime import date
import os

today = date.today()
string_today = str(today)

path = "/home/ubuntu/Desktop"
path_to_folder = path+"/Data/"+string_today

try:
	os.mkdir(path_to_folder)
except OSError:
	print "Creation failed"
else:
	print "Successfully created"

