# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 19:42:47 2022

@author: abbma
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 12:00:34 2022

@author: abbma
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 23:20:11 2022

@author: abbma
"""

import geopandas as gpd
import pandas as pd
from bokeh.models import ColumnDataSource, DateRangeSlider, Slider, CustomJS, HoverTool, ColorBar, LabelSet, Select, Scatter, LinearAxis
from bokeh.core.enums import MarkerType
from bokeh.plotting import figure, output_file
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from bokeh.io import curdoc, show
from bokeh.layouts import row, column
from bokeh.embed import components
from bokeh.transform import factor_cmap
import json
import requests
import numpy as np
from sqlalchemy import create_engine

data_map = data_map

### !!!Preprocessing data!!! ###

palette=["#29bbff","#f5ff1a","#ff211a"]

## Create count for number of point per zone per day ##
days = data_map['Date'].unique().tolist()

# Initialisation
index_day=[]

for j in range(len(days)) :
    index_day.append([])
    
count_class0 = []
count_class1 = []
count_class2 = []

#loop over day and zone
for j in range(len(days)) :
    i_0 = 0
    i_1 = 0
    i_2= 0
    for i in range(len(data_map['Date'])):
        if data_map['Date'][i]==days[j]:
            index_day[j].append(i)
            if data_map['Water_class'][i]==0:
                i_0 +=1
            elif data_map['Water_class'][i]==1:
                i_1 +=1
            elif data_map['Water_class'][i]==2:
                i_2 +=1
    count_class0.append(i_0)
    count_class1.append(i_1)
    count_class2.append(i_2)

#ordering everything in a dataframe
diag_data = pd.DataFrame()
diag_data['date']=pd.to_datetime(days)
diag_data['count class 0']=pd.to_numeric(count_class0)
diag_data['count class 1']=pd.to_numeric(count_class1)
diag_data['count class 2']=pd.to_numeric(count_class2)

diag_data = diag_data.sort_values(by=['date'])
#%%

p = figure(width=900, height=400, y_range = [-1,20],x_axis_type="datetime")
p.title.text = 'Number of area per day per bacteria class. (Click on legend entries to mute the corresponding lines)'

for data, name, color in zip(['count class 0','count class 1','count class 2'], ["low", "medium", "high"], palette):
    p.circle(diag_data['date'], diag_data[data], line_width=2, color=color, alpha=0.8,
           muted_color=color, muted_alpha=0.2, size = 15,
           legend_label=('Number of point with '+name+' bacteria level'))

p.legend.location = "top_left"
p.legend.click_policy="hide"

show(p)



