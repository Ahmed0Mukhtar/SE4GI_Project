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


#%%
engine = create_engine('postgresql://postgres:postgres@localhost:5432/se4g')

data = gpd.GeoDataFrame.from_postgis('PRWC', engine, geom_col='geometry').to_crs(3857)
#data = data.to_crs(3857)
#%%


data['x'] = data['geometry'].x
data['y'] = data['geometry'].y

data_map = data.drop('geometry', axis=1)

#%%



#%% Preparing the figure

#(b,d) = 41.795657, -72.860289
#(a,c) = 41.6333328,-73.3157797
#(a,b)_EPSG:3857 = (-8161475.26, -8110770.26), (c,d)_EPSG:3857 = (5106211.74, 5130418.82),
palette=["#29bbff","#f5ff1a","#ff211a"]

TOOLTIPS = [
    ("Reference gauge ", "@Nearest_USGS"),
    ("Bacteria level (MPN/100ml)", "@Bacteria_MPNper100ml"),
    ("Safe for ", "@Safe_uses")
    ]


colormap={i : palette[i] for i in [0,1,2]}
colors=[colormap[x] for x in data_map.Water_class]

data_map['colors']=colors

cds = ColumnDataSource(data_map)

MAP = figure(title='Bacteria Map', 
           width = 700, height = 700,
           x_range = (-8170850.62, -8131888.80), y_range = (5071521.81, 5116146.29),
           x_axis_type="mercator", y_axis_type="mercator", 
           tooltips=TOOLTIPS)

MAP.add_tile(get_provider(CARTODBPOSITRON))

#MAP.scatter(x='x', y='y', source=cds, marker="inverted_triangle", line_color='black', fill_color='colors', size = 20)


#Add Labels and add to the plot layout
labels = LabelSet(x='x', y='y', text='Index', level="glyph",
              x_offset=5, y_offset=5, source=cds, render_mode='css')

MAP.add_layout(labels)
#show(MAP)

#%% Dynamic Time selection

days = data_map['Date'].unique()

# Create Select Widget menu options
day_list=list(days)
options=[]
for i in day_list:
    string = str(i)
    options.append(string) 

        
#create witget options
select_day = Select(options = options, value=options[0],
                        title = 'Select an obsevation day')
slider = Slider(start=0, end =13, value=0, step=1, title = "choose a day")
update_map = CustomJS(args=dict(source=cds, slider=slider), code="""
    var data = source.data;
    var day_id= slider.value;
    var x = data['x']
    var y = data['y']
    
    source.change.emit();
""")
# Create a function that will be called when certain attributes on a widget are changed
def callback_select(attr, old, new):
    N=new
    tempdata = data_map.loc[data_map['Date']==N]
    temp_cds=ColumnDataSource(tempdata)
    cds.data=temp_cds.data
    MAP.scatter(x='x', y='y', source=cds, marker="inverted_triangle", line_color='black', fill_color='colors', size = 20)

select_day.on_change('value', callback_select)

#%%
layout = row(select_day, MAP)
show(layout)
curdoc().add_root(layout)

