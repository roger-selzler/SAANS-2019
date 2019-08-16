# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
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

DATAFOLDER = "/var/www/rawdata/data/"
TEMPFOLDER = os.path.expanduser('~/temp')
USERNAME = 'rogerselzler'
SERVER = '172.16.59.3'



minSliderBar = 0;
maxSliderBar = 0;

os.system('clear')


# ECGData = np.zeros(shape=(0,0))

# ECGData = [];
def execCommand(cmd):
	print("executing command: " + cmd)
	client = paramiko.SSHClient()
	host_keys = client.load_system_host_keys()
	client.connect(SERVER,username=USERNAME)
	stdin, stdout, stderr = client.exec_command(cmd)
	exitStatus = stdout.channel.recv_exit_status()
	if exitStatus == 0:
		print ("cmd \"" + cmd + "\" successfull.")
	else:
		print ("cmd \"" + cmd + "\" returned an error: " + str(exitStatus))
	client.close()
	

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
				cmd = 'scp ' + DATAFOLDER + subject + os.sep + session + os.sep + fileX + ' ' + USERNAME + '@172.16.59.24:' + TEMPFOLDER + os.sep + fileX
				print(cmd)
				execCommand(cmd)

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
    	dcc.Slider(
    		id='cur_time_slider',
    		min=minSliderBar,
    		max=maxSliderBar,
    		value=minSliderBar)
    	],style={
    		'columnCount':1,
    		'height':16
    	}),
    html.Div([
    	# html.Div([
    		html.I(id='stop_Btn', n_clicks=0, className='fa fa-stop',style={'padding':10}),
    		html.I(id='play_Btn', n_clicks=0, className='fa fa-play',style={'padding':10}),
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
		'textAlign':'center'
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
		# print(fig)
		# fig={
		# 'data': [
		# 	{
		# 		'x': ECGData['Time'].values,
		#         'y': ECGData['EcgWaveform'].values,
		#         'name': 'ECG'
		#     }],
		#     'layout': {
		#     	'height':350,
		#         'name':'tst name',
		#         'title':'Continuous time signals'
		#         }
	 #    	}
	except Exception as e:
		print('Error on creating figure')
		print(e)
		fig ={}
	
	return fig,minSliderBar,maxSliderBar
	


if __name__ == '__main__':
    app.run_server(debug=True)

