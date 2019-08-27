import pandas as pd
import numpy as np
import os
import re
# from datetime import datetime
import datetime

try:
    import readline
    import rlcompleter
    readline.parse_and_bind("tab: complete")
except ImportError:
    print("Module readline not available.")


# file  = '~/temp/1/2/20190610_1113_BREAKOUT_N01_SESSION_2_TR01.txt'

def readViconDataSession(file):
	sessionData = dict()
	f = open(os.path.expanduser(file),"r")
	strTime = f.readline()
	a = re.match(r'([0-9]+)_([0-9]+)',strTime)
	sessionData['startTime'] = datetime.datetime.strptime(a.group(0),'%Y%m%d_%H%M%S')
	skipRowsCount = 1;
	while True:
		strAux = f.readline()
		if "OS Time" in strAux:
			print "time to stop"
			break 
		skipRowsCount+=1
		print "skip rows count: " ,skipRowsCount
		if skipRowsCount >50:
			break
	f.close()
	data = pd.read_csv(file,delimiter='\t',skiprows=skipRowsCount)
	sessionData['time'] = []
	for i in data['Application Time (s)']:
		sessionData['time'].append(datetime.timedelta(seconds=i) + 
			sessionData['startTime'])
	sessionData['endTime'] = sessionData['time'][-1]
	sessionData['OS Time'] = data['OS Time']
	sessionData['Heart Rate'] = data['Heart Rate']
	sessionData['Breathing Rate'] = data['Breathing Rate']
	sessionData['sessionFile'] = file
	return sessionData

# data = readViconDataSession(file)
# print(list(data))
