# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# import packages
import json
import requests
import numpy as np
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine

"""DATABASE"""
# loads the raw data from the Epicollect5 API ,process it and cleans it to send it to the
# local server database management system postgreSQL

""" REQUEST FROM EPICOLLECT5 DATA """
"""-------------------------------"""
# send the request for the Dataset
response = requests.get('https://five.epicollect.net/api/export/entries/prwc-bacteria-sampling-2020?per_page=200')
# store the raw text of the response in a variable
raw_data = response.text
# converting the raw text response into a readable JSON format
data = json.loads(raw_data)
# from JSON dataset to Pandas DataFrame
whole_df = pd.json_normalize(data['data']['entries'])

#%%

""" DATA CLEANING """
"""---------------"""
# Remove unuseful data 
data_df = whole_df.drop(['ec5_uuid','created_at','uploaded_at', 'title','1_Samplers_First_Nam','16_Upstream_photo','17_Downstream_photo','18_Which_method_did_','21_Which_method_did_'], axis = 1)
# rename All Columns in the dataset //df.set_axis (['new_col1', 'new_col2', 'new_col3', 'new_col4'], axis='columns')//
data_df = data_df.set_axis(['Location_site', 'Sample_Type', 'Date', 'Time', 'Nearest_USGS', 'Streamflow_cfs', 'Sample:wet/dry', 'Weather_c', 'Airtemp_C', 'Water_level', 'Water_odor', 'Water_color', 'Observed_use', 'Watertemp_C', 'Conductivity_Scm', 'Obs/Comments', 'Bacteria_Lvl(MPN/100ml)', 'Nitrate(mg/L)', 'latitude', 'longitude', 'accuracy', 'UTM_Northing', 'UTM_Easting', 'UTM_Zone'], axis='columns')
# a back-up database is stored in a csv file
data_df.to_csv(r'C:/Users/abbma/Documents/Software/projet/test-ahmedClean_db.txt')

# creating new columns with numeric coordinate and accuracy values
data_df['latitude'] = pd.to_numeric(data_df['latitude'], errors='coerce')
data_df['longitude'] = pd.to_numeric(data_df['longitude'], errors='coerce')
data_df['accuracy'] = pd.to_numeric(data_df['accuracy'], errors='coerce')

# from Pandas DataFrame to GeoPandas GeoDataFrame
data_gdf = gpd.GeoDataFrame(data_df, geometry=gpd.points_from_xy(data_df.longitude, data_df.latitude))
# setting up the reference system for the geodesic coordinates in WGS84
data_gdf= data_gdf.set_crs(epsg=32618, inplace=True)

#%%

""" EXPORTING DATA TO DBMS """
"""------------------------"""
# setup db connection (generic connection path to be update with your credentials:
#'postgresql://postgres:postgres@localhost:5432/se4g')
engine = create_engine('postgresql://postgres:postgres@localhost:5432/se4g')

# data_df.to_sql('BRWC water quality monitoring', engine, if_exists = 'replace', index=False)
data_gdf.to_postgis('PRWC', engine, if_exists = 'replace', index=False)

#%%

clean_data = gpd.GeoDataFrame.from_postgis('PRWC', engine, geom_col='geometry')
clean_data.plot()