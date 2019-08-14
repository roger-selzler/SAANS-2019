# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
import base64
import paramiko
import re
import datetime
import csv
import os,sys
import pandas as pd

DATAFOLDER = "/var/www/rawdata/data/"
TEMPFOLDER = os.path.expanduser('~/temp')
USERNAME = 'rogerselzler'
SERVER = '172.16.59.3'


ECGData = [];
# def execCommand(cmd):
# 	print("executing command: " + cmd)
# 	# client.connect(SERVER,username=USERNAME)
# 	client = paramiko.SSHClient()
# 	host_keys = client.load_system_host_keys()
# 	client.connect(SERVER,username=USERNAME)
# 	stdin, stdout, stderr = client.exec_command(
# 		'ls -d ' + DATAFOLDER + '*/')
# 	client.close()
# 	SUBJECTS = []
# 	for line in stdout:
# 		print (line.strip('\n'))
# 		aux = line.split('/')
# 		aux = aux[len(aux)-2]
# 		# if aux.isdigit()
# 		SUBJECTS.append(aux)
# 	SUBJECTS = [ a for a in SUBJECTS if a.isnumeric() ]
# 	SUBJECTS.sort(key=float)
# 	print(SUBJECTS)
# 	return stdin,stdout,stderr;

def requestSubjects():
	client = paramiko.SSHClient()
	host_keys = client.load_system_host_keys()
	client.connect(SERVER,username=USERNAME)
	cmd = 'ls -d ' + DATAFOLDER + '*/'
	stdin, stdout, stderr = client.exec_command(cmd)
	SUBJECTS = []
	for line in stdout:
		# print (line.strip('\n'))
		aux = line.split('/')
		aux = aux[len(aux)-2]
		# if aux.isdigit()
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
		# if aux.isdigit()
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
	client = paramiko.SSHClient()
	host_keys = client.load_system_host_keys()
	client.connect(SERVER,username=USERNAME)
	if type(filename) == list:
		for fileX in filename:
			if not os.path.isfile(TEMPFOLDER + os.sep + fileX):
				print ('downloading file: ' + fileX)
				print(TEMPFOLDER + os.sep + fileX)
				print(DATAFOLDER + subject + os.sep + session + os.sep + fileX)
				cmd = 'scp ' + DATAFOLDER + subject + os.sep + session + fileX + ' ' + USERNAME + '@172.16.59.24:' + TEMPFOLDER + os.sep + fileX
				print(cmd)
				stdin, stdout, stderr = client.exec_command(cmd) 
			else:
				print (fileX + " already exist!")
	elif type(filename) == str:
		print ('downloading file: ' + filename)
		print(TEMPFOLDER + os.sep + filename)
	client.close()

	

def loadData(subject, session,files):
	print('Loading files' )
	# re.match(pattern, string)
	ecgfiles =[];
	for i in files:
		if 'ECG.csv' in i:
			# print (i)
			ecgfiles.append(i)
	if len(ecgfiles) > 0:
		print(ecgfiles[0])
	print(type(ecgfiles))
	downloadFiles(subject, session, ecgfiles)
	ECGData = [];

	# with open(ecgfiles[0]) as csv_file:
	# 	csv_reader = csv.reader(csv_file,delimiter=',')
	# 	line_count=0
	# 	for row in csv_reader:
	# 		if line_count==0:
	# 			printf('column names are {", ".join(row)}')

	# for i in files:
	# 	print(i)




SUBJECTS = requestSubjects()

# -- configuration of the layout
external_stylesheets = [
'https://codepen.io/chriddyp/pen/bWLwgP.css',
'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# app.css.append_css({'external_url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'})

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
	    ],style={'columnCount':4}), # set to 2 for full page
    html.Div([
    	dcc.Graph(
    		id='timeSeriesGraph'
    		)
    	]
    	),
    html.Div([
    	dcc.Slider(
    		id='cur_time',
    		min=0,
    		max=100,
    		value=50)
    	],style={
    		'columnCount':1,
    		'height':16
    	}),
    html.Div([
    	# html.Div([
    		html.I(id='play_Btn', n_clicks=0, className='fa fa-play',style={'padding':10}),
    		# ],style={'padding':10}),
    	# html.Div([
    		html.I(id='fast_backward_Btn', n_clicks=0, className='fa fa-fast-backward',style={'padding':10}),
    		html.I(id='backward_Btn', n_clicks=0, className='fa fa-backward',style={'padding':10}),
    		html.I(id='pause_Btn', n_clicks=0, className='fa fa-pause',style={'padding':10}),
    		html.I(id='forward_Btn', n_clicks=0, className='fa fa-forward',style={'padding':10}),
    		html.I(id='fast_forward_Btn', n_clicks=0, className='fa fa-fast-forward',style={'padding':10}),
    		html.I(id='decreaseXlim_Btn', n_clicks=0, className='fa fa-minus',style={'padding':10}),
    		html.I(id='increaseXlim_Btn', n_clicks=0, className='fa fa-plus',style={'padding':10})
    		
    		# ],style={'padding':10}),
	   #  html.Div([html.I(id='pauseBtn', n_clicks=0, className='fa fa-pause')],'style'={'padding':10}),
	   #  html.Div([html.I(id='submit-button', n_clicks=0, className='fa fa-play')],'style'={'padding':10})
	   #  ],style={
	   #  'align-items':'center',
	   #  'padding':100
		],style={
		'columnCount':1,
		'text-align':'center'
		}),
    html.Div(id='messageContainer',children='test'),
    # html.Div(id='hiddenListOfFiles',style={'display':'true','columnCount':3}),
    html.Div(id='xAxisLimValue',children=30,style={'display':'true','columnCount':3}),
	html.Div(id='hiddenListOfFiles',style={'display':'true','columnCount':3})
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

# @app.callback(Output('messageContainer','children'),
# 	[Input('session','value')])
# def updateMessage(input):
# 	if type(input) == list:
# 		print("is list!!!")
# 		# print(s)
# 	else:
# 		s=input
# 	print(type(s))
# 	print(s)
# 	return html.Div(s)

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

@app.callback(Output('timeSeriesGraph','figure'),
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

	fig={
	'data': [
		{
			'x': [1, 2, 3, 4],
	        'y': [4, 1, 3, 5],
	        'text': ['a', 'b', 'c', 'd'],
	        'customdata': ['c.a', 'c.b', 'c.c', 'c.d'],
	        'name': 'Trace 1',
	        'mode': 'markers',
	        'marker': {'size': 12}
	    },
	    {
	        'x': [1, 2, 3],
	        'y': [9, 4, 1],
	        'text': ['w', 'x', 'y'],
	        'customdata': ['c.w', 'c.x', 'c.y'],
	        'name': 'Trace 2',
	        'mode': 'markers',
	        'marker': {'size': 14}
	    }
	    ],
	    'layout': {
	        'clickmode': 'event+select',
	        'height':350
	    }
    }
	return fig


if __name__ == '__main__':
    app.run_server(debug=True)

