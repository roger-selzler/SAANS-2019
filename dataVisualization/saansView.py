#! /usr/bin/python
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input,Output,State
import base64
import paramiko
import re
from datetime import datetime
import time
import csv
import os,sys,getopt
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import random
import socket
import webbrowser 

os.system('clear')


DATAFOLDER = "/var/www/rawdata/data/"
TEMPFOLDER = os.path.expanduser('~/temp')
SERVER = 'saans.ca'
PORT = None

FIXEDPORT = False # used to debug or open new window
DEBUGMODE = True # if true, it updates the browser when the code changes.

AGILEMODE = True
if AGILEMODE:
	MAXSIGNALLENGTH = -10000 # -1 for the entire length
	MINSIGNALLENGTH = -12000
else:
	MAXSIGNALLENGTH = -1 # -1 for the entire length
	MINSIGNALLENGTH = 0

minSliderBar = 0;
maxSliderBar = 0;
ECGData=pd.DataFrame()
BreathingData=pd.DataFrame()
# timeSeriesFig = go.Figure()
# -- options for running this file.
try:
	opts,args = getopt.getopt(sys.argv[1:], "hu:p:",["username=","port="])
	# print(opts)
	# print(args)
except getopt.GetoptError:
	print('saansView.py -u <username> -p <port>')
	sys.exit(2)
for opt, arg in opts:
	if opt in ('-h','help'):
		print('saansView.py -u <username> -p <port>')
		sys.exit(2)
	elif opt in ('-u','--username'):
		USERNAME = arg
	elif opt in ('-p','--port'):
		PORT = arg
	print(' ')



# -- Create a port and check if it is being used. 
def selectPort():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	while True:
		PORT = random.randint(8000, 10000)
		result = sock.connect_ex(('localhost',PORT))
		if result == 0:
			print "Port " + str(PORT) + " is in use."
			sock.close()			
		else:
			print "Port " + str(PORT) + " is available."
			sock.close()
			break
	return PORT 

def execCommand(cmd):
	print("executing command: " + cmd)
	client = paramiko.SSHClient()
	host_keys = client.load_system_host_keys()
	client.connect(SERVER,username=USERNAME)
	stdin, stdout, stderr = client.exec_command(cmd)
	exitStatus = stdout.channel.recv_exit_status()
	if exitStatus == 0:
		print ("cmd \"" + cmd + "\" successfull.")
		status = 0
	else:
		print ("cmd \"" + cmd + "\" returned an error: " + str(exitStatus) + "\n\n\n")
		status = 1
		
	client.close()
	return status

def requestSubjects():
	client = paramiko.SSHClient()
	host_keys = client.load_system_host_keys()
	client.connect(SERVER,username=USERNAME)
	cmd = 'ls -d ' + DATAFOLDER + '*/'
	stdin, stdout, stderr = client.exec_command(cmd)
	SUBJECTS = []
	for line in stdout:
		aux = line.split('/')
		aux = aux[len(aux)-2]
		SUBJECTS.append(aux)
	SUBJECTS = [ a for a in SUBJECTS if a.isnumeric() ]
	SUBJECTS.sort(key=float)
	client.close()
	return SUBJECTS

def requestSessions(subject):
	client = paramiko.SSHClient()
	host_keys = client.load_system_host_keys()
	client.connect(SERVER,username=USERNAME)
	cmd = 'ls -d ' + DATAFOLDER + subject + '/*/'
	stdin, stdout, stderr = client.exec_command(cmd) 
	SESSIONS = []
	for line in stdout:
		# print (line.strip('\n'))
		aux = line.split('/')
		aux = aux[len(aux)-2]
		SESSIONS.append(aux)
	SESSIONS = [ a for a in SESSIONS if a.isnumeric() ]
	SESSIONS.sort(key=float)
	sessionoptions = []
	for i in SESSIONS: 
		sessionoptions.append({'label':str(i),'value':str(i)})
	client.close()
	return sessionoptions

def requestListOfFiles(subject,session):
	client = paramiko.SSHClient()
	host_keys = client.load_system_host_keys()
	client.connect(SERVER,username=USERNAME)
	cmd = 'ls ' + DATAFOLDER + subject + os.sep + session
	stdin, stdout, stderr = client.exec_command(cmd) 
	FILES = []
	for line in stdout:
		FILES.append(line.strip('\n'))
	client.close()
	return FILES

def downloadFiles(subject,session,filename):
	if not os.path.isdir(TEMPFOLDER):
		print('Folder ' + TEMPFOLDER + ' does not exist')
		os.mkdir(TEMPFOLDER,0755)
	if type(filename) == list:
		for fileX in filename:
			if not os.path.isfile(TEMPFOLDER + os.sep + fileX):
				print ('downloading file: ' + fileX)
	# print(TEMPFOLDER + os.sep + fileX)
	# print(DATAFOLDER + subject + os.sep + session + os.sep + fileX)
	# cmd = 'scp ' + USERNAME + '@' + SERVER + ':' + DATAFOLDER + subject + os.sep + session + os.sep + fileX + ' ' + TEMPFOLDER + os.sep + fileX
	# print(cmd)
	# status = execCommand(cmd)
	# if status != 0:
	# print ('Command execution returned status ' + str(status))
				try:
					client = paramiko.SSHClient()
					host_keys = client.load_system_host_keys()
					client.connect(SERVER,username=USERNAME)
					ftpClient = client.open_sftp()
					ftpClient.get(DATAFOLDER + subject + os.sep + session + os.sep + fileX,
						TEMPFOLDER + os.sep + fileX)
					ftpClient.close()
					client.close()
				except Exception as e:
					print(e)
	

			else:
				print (fileX + " already exist!") 
	elif type(filename) == str:
		print ('downloading file: ' + filename)
		print(TEMPFOLDER + os.sep + filename)

def loadData(subject, session,files):
	print('Loading files' )
	# ecgfiles = [];
	global ECGData,BreathingData
	filesForDownload = [];	
	matchers = ['ECG.csv','Breathing.csv']
	filesForDownload = [s for s in files if any(ss in s for ss in matchers)]
	downloadFiles(subject, session, filesForDownload)
	# print(str(type(filesForDownload)))
	for fileX in filesForDownload:
		if os.path.isfile(TEMPFOLDER + os.sep + fileX):
			if 'ECG.csv' in fileX:
				print ('Loading ' + fileX + ' into ECGData')
				ECGData = pd.read_csv(TEMPFOLDER + os.sep + fileX)
				ECGData['Time']=pd.to_datetime(ECGData['Time'],format="%d/%m/%Y %H:%M:%S.%f")
				print('Format of ECGData is ' + str(type(ECGData)) + 
				 ', with size: ' + str(ECGData.size))
			elif 'Breathing.csv' in fileX:
				print ('Loading ' + fileX + ' into BreathingData')
				BreathingData = pd.read_csv(TEMPFOLDER + os.sep + fileX)
				BreathingData['Time']=pd.to_datetime(BreathingData['Time'],format="%d/%m/%Y %H:%M:%S.%f")
				print(list(BreathingData))
				print('Format of BreathingData is ' + str(type(BreathingData)) + 
				 ', with size: ' + str(BreathingData.size))
		
	
	if ECGData.size == 0:
		minSliderBar = 0
		maxSliderBar = 1
	else:
		minSliderBar = ECGData['Time'].iloc[0]
		maxSliderBar = ECGData['Time'].iloc[-1]
	print ('Finished loading data')
	# for i in files:
	# 	if 'ECG.csv' in i:
	# 		filesForDownload.append(i)
	# 		ecgfiles.append(i)
	# 		# print(filesForDownload)
	# if len(ecgfiles) > 0:
	# 	print(ecgfiles[0])
	# downloadFiles(subject, session, ecgfiles)
	# if len(ecgfiles) > 0:
	# 	print("length of ecgfiles is: " + str(len(ecgfiles)))
	# 	if os.path.isfile(TEMPFOLDER + os.sep + ecgfiles[0]):	
	# 		ECGData = pd.read_csv(TEMPFOLDER + os.sep + ecgfiles[0])
	# 		ECGData['Time']=pd.to_datetime(ECGData['Time'],format="%d/%m/%Y %H:%M:%S.%f")
	# 		# print(ECGData.head())
	# 		# print(type((ECGData['Time'])))
	# 		# ECGData['Time'] = time.mktime(datetime.datetime.strptime(pd.Series.to_string(ECGData['Time']),"%d/%m/%Y %H:%M:%S.%f"))
	# 		# print(ECGData.head())
	# 	else:
	# 		ECGData = None
	# 	# DATE = [(datetime.strptime(x,"%d/%m/%Y %H:%M:%S.%f")) for x in ECGData['Time']]
	# 	# ECGData['Time']=pd.Series([time.mktime(x.timetuple()) + x.microsecond/1e6 for x in DATE])
	# 	print(ECGData.head())

		

	
def prepareFigures():
	print('Preparing figures to plot')
	fig = go.Figure()
	try:
		print('Preparing ECG trace')
		print('Size: '+ str(ECGData.size))
		fig.add_trace(
			go.Scatter(
				x=ECGData['Time'].iloc[MINSIGNALLENGTH:MAXSIGNALLENGTH],
				y=ECGData['EcgWaveform'].iloc[MINSIGNALLENGTH:MAXSIGNALLENGTH],
				name='ECG',
				mode='lines'))
	except Exception as e:
		print(e)

	try:
		print('Preparing Breathing trace')
		print('Size: '+ str(BreathingData.size))
		fig.add_trace(
			go.Scatter(
				# x=BreathingData['Time'].iloc[int(MINSIGNALLENGTH/10):int(MAXSIGNALLENGTH/10)],
				# y=BreathingData['BreathingWaveform'].iloc[int(MINSIGNALLENGTH/10):int(MAXSIGNALLENGTH/10)],
				x=BreathingData['Time'],
				y=BreathingData['BreathingWaveform'],
				name='Breathing',
				# mode = 'lines+markers'))
				mode = 'lines'))
	except Exception as e:
		print(e)
	
	print('Updating layout')
	fig.update_layout(
		title="Time Series Data"
		)
	print('Figures prepared. Returning figures to plot.')
	return fig.to_dict()



SUBJECTS = requestSubjects()

# -- configuration of the layout
external_stylesheets = [
	'https://codepen.io/chriddyp/pen/bWLwgP.css',
	'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
	]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
	html.Div(
		html.H1('SAANS visualization tool'),
		style={'text-align':'center'}),
	html.Div([
	    html.Label('Subject'),
	    dcc.Dropdown (id='subject',
	    		options=[
	    		{'label':i,'value': i} for i in SUBJECTS],
	    		value='1'
	    	),
		html.Label('Session'),  
	    dcc.Dropdown (id='session')
	    ],style={'columnCount':2}), # set to 2 for full page
	html.Nav([
		html.Div([
			html.I(id='stop_Btn', n_clicks=0, className='fa fa-stop',style={'padding':10}),
			html.I(id='play_Btn', n_clicks=0, className='fa fa-play',style={'padding':10}),
			html.I(id='fast_backward_Btn', n_clicks=0, className='fa fa-fast-backward',style={'padding':10}),
			html.I(id='backward_Btn', n_clicks=0, className='fa fa-backward',style={'padding':10}),
			html.I(id='pause_Btn', n_clicks=0, className='fa fa-pause',style={'padding':10}),
			html.I(id='forward_Btn', n_clicks=0, className='fa fa-forward',style={'padding':10}),
			html.I(id='fast_forward_Btn', n_clicks=0, className='fa fa-fast-forward',style={'padding':10}),
			html.I(id='decreaseXlim_Btn', n_clicks=0, className='fa fa-minus',style={'padding':10}),
			html.I(id='increaseXlim_Btn', n_clicks=0, className='fa fa-plus',style={'padding':10})
			],style={'text-align':'center','width':'100%'}),
		html.Div([
			dcc.Slider(
    		id='cur_time_slider',
    		min=minSliderBar,
    		max=maxSliderBar,
    		value=minSliderBar)
    		],style={'width':'90%','text-align':'center','margin-left':'5%'})
		],style={
		'position':'sticky',
		'top':'0'
		# 'text-align':'center',
		# 'bottom':'0','border':'1px solid','width':'90%','background-position': 'top','background-color':'green'
		}),		
    html.Div([
    	dcc.Graph(
    		id='timeSeriesGraph',
    		figure={
    			'layout': {
			        # 'clickmode': 'event+select',
			        'height':350,
			        'name':'tst name',
			        'title':'Continuous time signals'
			    }
    		}
    		)
    	],
    	),    
    html.Div([
    	dbc.Button("List of files",id='buttonListOfFiles'),
    	dbc.Modal([
    		dbc.ModalHeader("List of Files"),
    		dbc.ModalBody([
    			html.Div(id='hiddenListOfFiles',style={'display':'true','columnCount':1})
    			]),
    		dbc.Button("Close",id='closehiddenListOfFiles',className='ml-auto')
    		],id='listOfFilesDialog',is_open=False)
    	]),
	html.Div(id='messageContainer',children='test'),
    # html.Div(id='hiddenListOfFiles',style={'display':'true','columnCount':3}),
    html.Div(id='xAxisLimValue',children=30,style={'display':'true','columnCount':2}),
    html.Div([
    	dcc.Graph(
    		id='timeSeriesGrap2h',
    		figure={
    			'layout': {
			        # 'clickmode': 'event+select',
			        'height':350,
			        'name':'tst name',
			        'title':'Continuous time signals'
			    }
    		}
    		)
    	],
    	),
	])

# -- Adjust the time displayed on the ECG graph
@app.callback(Output('xAxisLimValue','children'),
	[Input('increaseXlim_Btn','n_clicks'),
	Input('decreaseXlim_Btn','n_clicks')])
def increaseTimeSeriesDataLim(increase,decrease):
	cval = 30 + 5*increase - 5*decrease
	# print(cval)
	return cval

@app.callback(Output('hiddenListOfFiles','children'),
	[Input('subject','value'),
	Input('session','value')])
def storeFileNames(subject, session):
	FILES = requestListOfFiles(str(subject),str(session))
	s= [html.Div(id=fileN,children=fileN) for fileN in FILES]
	# print(type(s))
	return(s)



# https://dash.plot.ly/live-updates
@app.callback(
	[Output('session','options'),
	Output('session','value')],
	[Input('subject','value')],
	)
def updateSessionList(subjectSelected):
	# print(subjectSelected)
	sessionoptions = requestSessions(subjectSelected)
	# print(sessionoptions) 
	if (len(sessionoptions) > 0):
		sessionval = sessionoptions[0]['value']
	else:
		sessionval = '0'
	# print(len(sessionoptions))

	return sessionoptions,sessionval

@app.callback([
	Output('timeSeriesGraph','figure'),
	Output('cur_time_slider','min'),
	Output('cur_time_slider','max')],
	[Input('subject','value'),
	Input('session','value')])
def updateGraphs(subject,session):
	FILES = requestListOfFiles(str(subject),str(session))
	t1 = time.time()
	loadData(str(subject),str(session),FILES)
	t2 = time.time()
	try:
		tfig = prepareFigures()		
	except Exception as e:
		print('Error on creating figure')
		print(e)
		tfig =go.Figure().to_dict()
	print('Sending files to webbrowser')
	return tfig,minSliderBar,maxSliderBar

@app.callback(Output('listOfFilesDialog','is_open'),
	[Input('buttonListOfFiles','n_clicks'),
	Input('closehiddenListOfFiles','n_clicks')],
	[State('listOfFilesDialog','is_open')],
	)
def toggleListOfFilesDialog(i1,i2,is_open):
	if i1 or i2:
		return not is_open
	return is_open


if (not FIXEDPORT) and PORT == None:
	PORT = selectPort()
	# webbrowser.open('localhost:' + str(PORT))
elif PORT == None:
	PORT = 8050

if __name__ == '__main__':
	app.run_server(debug=DEBUGMODE,port=PORT)
    

