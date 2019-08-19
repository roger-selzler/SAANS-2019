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
import os,sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import random
import socket
import webbrowser

DATAFOLDER = "/var/www/rawdata/data/"
TEMPFOLDER = os.path.expanduser('~/temp')
USERNAME = 'rogerselzler'
# SERVER = '172.16.59.3'
SERVER = 'saans.ca'
FIXEDPORT = True # used to debug or open new window
DEBUGMODE = True

minSliderBar = 0;
maxSliderBar = 0;

# os.system('clear')

# -- Create a port and check if it is being used. 
PORT = 8050
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
				print(TEMPFOLDER + os.sep + fileX)
				print(DATAFOLDER + subject + os.sep + session + os.sep + fileX)
				cmd = 'scp ' + USERNAME + '@' + SERVER + ':' + DATAFOLDER + subject + os.sep + session + os.sep + fileX + ' ' + TEMPFOLDER + os.sep + fileX
				print(cmd)
				status = execCommand(cmd)
				if status != 0:
					print ('Command execution returned status ' + str(status))
					client = paramiko.SSHClient()
					host_keys = client.load_system_host_keys()
					client.connect(SERVER,username=USERNAME)
					ftpClient = client.open_sftp()
					ftpClient.get(DATAFOLDER + subject + os.sep + session + os.sep + fileX,
						TEMPFOLDER + os.sep + fileX)
					ftpClient.close()
					client.close()
	

			else:
				print (fileX + " already exist!") 
	elif type(filename) == str:
		print ('downloading file: ' + filename)
		print(TEMPFOLDER + os.sep + filename)

def loadData(subject, session,files):
	print('Loading files' )
	ecgfiles =[];
	global ECGData
	ECGData = None
	for i in files:
		if 'ECG.csv' in i:
			ecgfiles.append(i)
	if len(ecgfiles) > 0:
		print(ecgfiles[0])
	downloadFiles(subject, session, ecgfiles)
	if len(ecgfiles) > 0:
		print("length of ecgfiles is: " + str(len(ecgfiles)))
		if os.path.isfile(TEMPFOLDER + os.sep + ecgfiles[0]):	
			ECGData = pd.read_csv(TEMPFOLDER + os.sep + ecgfiles[0])
			print(ECGData.head())
			# print(type((ECGData['Time'])))
			# ECGData['Time'] = time.mktime(datetime.datetime.strptime(pd.Series.to_string(ECGData['Time']),"%d/%m/%Y %H:%M:%S.%f"))
			# print(ECGData.head())
		else:
			ECGData = None
		DATE = [(datetime.strptime(x,"%d/%m/%Y %H:%M:%S.%f")) for x in ECGData['Time']]
		ECGData['Time']=pd.Series([time.mktime(x.timetuple()) + x.microsecond/1e6 for x in DATE])
		print(ECGData.head())

		minSliderBar = ECGData['Time'].iloc[0]
		maxSliderBar = ECGData['Time'].iloc[-1]
			


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
    # html.Div([
    # 	dcc.Graph(
	   #      id= '3DGraph' ,
	   #      figure={
	   #      	'layout': {
			 #        # 'clickmode': 'event+select',
			 #        # 'height':350,
			 #        # 'width':350,
			 #        'mode':'lines',
			 #        'name':'tst name',
			 #        'title':'3D Movement'
			 #        # 'textAlign':'center'
			 #    }
    # 		}
	   #  )
    # 	],style={'textAlign':'center',
    # 		'width':'50%',
    # 		'backgroundColor':'blue'}
    # ),
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
    		],id='listOfFilesDialog',is_open=True)
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
	loadData(str(subject),str(session),FILES)
	# print(value)
	# print(type(subject))
	# print(type(session))
	# print(FILES)
	# updateMessage('test new...')
	try:
		print (type(np.arange(ECGData['EcgWaveform'].size)))
		print (type(ECGData['EcgWaveform'].values))

		fig=dict(
			data=[dict(
				x=ECGData['Time'].values,
				y=ECGData['EcgWaveform'].values,
		        name='ECG'
				),
				dict(
				type='scatter',
				x=ECGData['Time'].values,
				y=ECGData['EcgWaveform'].values+10,
		        name='ECG12'
				)],
			layout=dict(
				height=350,
				name='tst name',
				title='Continuous time signals')
			)
		
	except Exception as e:
		print('Error on creating figure')
		print(e)
		fig ={}
	
	return fig,minSliderBar,maxSliderBar

@app.callback(Output('listOfFilesDialog','is_open'),
	[Input('buttonListOfFiles','n_clicks'),
	Input('closehiddenListOfFiles','n_clicks')],
	[State('listOfFilesDialog','is_open')],
	)
def toggleListOfFilesDialog(i1,i2,is_open):
	if i1 or i2:
		return not is_open
	return is_open

# try:
# execCommand('firefox \'localhost:' + str(PORT) + '\' &')
if not FIXEDPORT:
	PORT = selectPort()
	webbrowser.open('localhost:' + str(PORT))

if __name__ == '__main__':
	app.run_server(debug=DEBUGMODE,port=PORT)
    

