# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 23:20:11 2022

@author: abbma
"""

import geopandas as gpd
from bokeh.models import ColumnDataSource, LabelSet, Scatter, LinearAxis
from bokeh.core.enums import MarkerType
from bokeh.plotting import figure, output_file
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from bokeh.io import output_notebook, show
import json
import requests
import numpy as np
from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:postgres@localhost:5432/se4g')

data = gpd.GeoDataFrame.from_postgis('PRWC', engine, geom_col='geometry')
data1 = data.to_crs(3857)
#%%

data['x'] = data['geometry'].x
data['y'] = data['geometry'].y

data2 = data.drop('geometry', axis=1)

#%%
from bokeh.tile_providers import get_provider, Vendors

(b,d) = (-8179985.018966 ,5168610.699289)
(a,c) = (-7994090.166177, 5044905.024842)
#x_range = (-8179985, -7994090), y_range = (5044905, 5168610),

TOOLTIPS = [
    ("index", "$index"),
    ("flow", "@Streamflow_cfs"),
    ]

Psource = ColumnDataSource(data = data2)

P = figure(title='Streamflow Map', 
           width = 600, height = 600,
            
           x_axis_type="mercator", y_axis_type="mercator", 
           tooltips=TOOLTIPS)
P.add_tile(get_provider(CARTODBPOSITRON))

P.scatter(x=data2['x'], y=data2['y'], marker = 'inverted_triangle', size = 20)

#P.circle(x=data2['x'], y = data2['y'], color='red', radius=10) #size=10
show(P)

