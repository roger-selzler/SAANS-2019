# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
import base64
import paramiko
import re

DATAFOLDER = "/var/www/rawdata/data/"
USERNAME = 'rogerselzler'
SERVER = '172.16.59.3'
	
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
		print (line.strip('\n'))
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
		print (line.strip('\n'))
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
    		html.I(id='fast_forward_Btn', n_clicks=0, className='fa fa-fast-forward',style={'padding':10})
    		
    		# ],style={'padding':10}),
	   #  html.Div([html.I(id='pauseBtn', n_clicks=0, className='fa fa-pause')],'style'={'padding':10}),
	   #  html.Div([html.I(id='submit-button', n_clicks=0, className='fa fa-play')],'style'={'padding':10})
	   #  ],style={
	   #  'align-items':'center',
	   #  'padding':100
		],style={
		'columnCount':1,
		'text-align':'center'
		})
    ])


# @app.callback(dash.dependencies.Output)



@app.callback(
	[Output('session','options'),
	Output('session','value')],
	[Input('subject','value')],
	)
def updateSessionList(subjectSelected):
	print(subjectSelected)
	sessionoptions = requestSessions(subjectSelected)
	print(sessionoptions) 
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
	# print(value)
	
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
	        'height':300
	    }
    }
	return fig


if __name__ == '__main__':
    app.run_server(debug=True)

