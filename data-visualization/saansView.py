# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
import base64
import paramiko
import re

USERNAME = 'rogerselzler'
SERVER = '172.16.59.3'
DATAFOLDER = "/var/www/rawdata/data/"

client = paramiko.SSHClient()
host_keys = client.load_system_host_keys()
client.connect(SERVER,username=USERNAME)


stdin, stdout, stderr = client.exec_command(
    'ls -d ' + DATAFOLDER + '*/'
)

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



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

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
    dcc.Dropdown (id='session',
    		options=[
    		{'label':'1','value': '1'},
    		{'label':'2','value': '2'},
    		{'label':'3','value': '3'}
    		],
    		value='1'
    	)
    ],style={'columnCount':2})
    ],style={'columnCount':1})


# @app.callback(dash.dependencies.Output)



@app.callback(
	Output('session','value'),
	[Input('subject','value')],
	)
def updateSessionList(subject):
	host_keys = client.load_system_host_keys()
	client.connect(SERVER,username=USERNAME)
	stdin, stdout, stderr = client.exec_command(
	    'ls -d ' + DATAFOLDER + '*/'
	)

	SESSIONS = []
	for line in stdout:
		print (line.strip('\n'))
		aux = line.split('/')
		aux = aux[len(aux)-2]
		# if aux.isdigit()
		SESSIONS.append(aux)

	SESSIONS = [ a for a in SESSIONS if a.isnumeric() ]
	SESSIONS.sort(key=float)
	client.close()
	return {

	}

if __name__ == '__main__':
    app.run_server(debug=True)

