#!/usr/bin/python
import os
import time
from datetime import datetime
import pandas as pd 
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
try:
    import readline
    import rlcompleter
    readline.parse_and_bind("tab: complete")
except ImportError:
    print("Module readline not available.")
TEMPFOLDER = os.path.expanduser('~/temp')


# print()

# s = [   '07/06/2019 11:18:26.431',
#         '07/06/2019 11:18:26.435',
#         '07/06/2019 11:18:26.439'] 
# s=pd.Series(s)
# print(s)
# print(type(s))

# #time.mktime(datetime.datetime.strptime(s,"%d/%m/%Y %H:%M:%S.%f"))
# #datetime.datetime.strptime
# DATE = [(datetime.strptime(x,"%d/%m/%Y %H:%M:%S.%f")) for x in s] 
# print(type(DATE))
# # DATE  = [time.mktime(x) for x in DATE]
# print(type(DATE))
# for i in DATE:
#     print(time.mktime(i.timetuple()))
#     print(datetime.time(i))
#     # print(datetime.timestamp(datetime.now()))

# # a = dict(type='buttons',
# #                   showactive=False,
# #                   y=1,
# #                   x=1.3,
# #                   xanchor='right',
# #                   yanchor='top',
# #                   pad=dict(t=0, r=10),
# #                   buttons=[dict(label='Play',
# #                                 method='animate',
# #                                 args=[
# #                                     None,
# #                                     dict(frame=dict(duration=70, redraw=False),
# #                                          transition=dict(duration=0),
# #                                          fromcurrent=True,
# #                                          mode='immediate')
# #                                 ])])
# # print(type(a))
# # print(a)



# fig=dict(
# 	data=dict(
# 		x='datax',
# 		y='datay'),
# 	layout=''
# 	)
# print(fig)
# for i in list([fig]):
# 	print(i)



# filename = '2019_06_07-11_18_26_ECG.csv' 
# ECGData = pd.read_csv('/home/rogerselzler/1/1/' + filename)
# # print(type(ECGData))
# # print(ECGData.head())
# # DATE = [(datetime.strptime(x,"%d/%m/%Y %H:%M:%S.%f")) for x in ECGData['Time']]
# # TIME = pd.Series([time.mktime(x.timetuple()) + x.microsecond/1e6 for x in DATE])
# # # ecg = np.genfromtxt('/home/rogerselzler/1/1/' + filename,delimiter=',')
# ECGData['Time']=pd.to_datetime(ECGData['Time'],format="%d/%m/%Y %H:%M:%S.%f")
# # iris=px.data.iris()

# # fig = px.scatter(iris,x=ECGData['EcgWaveform'].values,y='sepal_length')
# fig = go.Figure()

# fig.add_trace(go.scatter.Line(x=ECGData['Time'].iloc[1:10],y=ECGData['EcgWaveform'].iloc[1:10],name='ECG'))
# fig.add_trace(go.Scatter(x=ECGData['Time'].iloc[1:10],y=ECGData['EcgWaveform'].iloc[1:10]+8000,name='ECG2'))
# fig.update_layout(
# 	title="title tst 2"
# 	)

# print(fig)
# print(fig.to_dict())
# fig.show()



from annotations import Annotation

ann = Annotation()

# os.system('clear')
# import json

# with open(TEMPFOLDER + os.sep + 'annotations.json',"r") as f:
# 	ann = json.load(f)
# print(list(ann))
# print(ann)


# with annX in ann:
# 	print(list(ann))