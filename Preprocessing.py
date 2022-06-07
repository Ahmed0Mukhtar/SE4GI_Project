# -*- coding: utf-8 -*-
"""
@author: Group7

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
data_df = data_df.set_axis(['Location', 'Sample:regular', 'Date', 'Time', 'Nearest_USGS', 'Streamflow_cfs', 'Sample:wet', 'Weather', 'Air_temp_C', 'Water_level', 'Water_odor', 'Water_color', 'Observed_use', 'Water_temp_C', 'Conductivity_Scm', 'Comments', 'Bacteria_MPNper100ml', 'Nitrate_mgperL', 'latitude', 'longitude', 'accuracy', 'UTM_Northing', 'UTM_Easting', 'UTM_Zone'], axis='columns')

# creating new columns with numeric coordinate and accuracy values
data_df['latitude'] = pd.to_numeric(data_df['latitude'], errors='coerce')
data_df['longitude'] = pd.to_numeric(data_df['longitude'], errors='coerce')
data_df['accuracy'] = pd.to_numeric(data_df['accuracy'], errors='coerce')
#data_df['Date'] = pd.to_datetime(data_df['Date'], errors='coerce')

data_df = data_df.loc[data_df['accuracy']<=5]
data_df = data_df.sort_values(by=['Date'], ascending=True)
#removing weird values from bacteria concentration column
data_clean=data_df
data_clean['Bacteria_MPNper100ml'] = data_df['Bacteria_MPNper100ml'].mask(data_df['Bacteria_MPNper100ml']=='2420+',2420)
data_clean['Bacteria_MPNper100ml'] = pd.to_numeric(data_clean['Bacteria_MPNper100ml'], errors='coerce')
data_clean  = data_clean.fillna(0)

#%%
#creating a function for classifying water per bacteria concentration
def waterclass(val):
    if val<=235:
        return 0
    elif 235<val<=575:
        return 1
    elif 575<val :
        return 2
    
data_clean['Water_class']=data_clean.apply(lambda row: waterclass(row['Bacteria_MPNper100ml']),axis=1)

#creating a function for classifying water per bacteria concentration
def wateruses(val):
    if val == 0:
        return 'Swimming','Wading','Fishing','Boating'
    elif val == 1:
        return 'Boating','Fishing'
    elif val==2 :
        return 'Danger ! Unsafe for swimming, boating, fishing or wading'

data_clean['Safe_uses']=data_clean.apply(lambda row: wateruses(row['Water_class']),axis=1)


#%%

# a back-up database is stored in a csv file
data_clean.to_csv(r'C:/Users/abbma/Documents/Software/projet/test-ahmedClean_db.txt')

# from Pandas DataFrame to GeoPandas GeoDataFrame
data_gdf = gpd.GeoDataFrame(data_clean, geometry=gpd.points_from_xy(data_clean['longitude'], data_clean['latitude']), crs="EPSG:4326")
# setting up the reference system for the geodesic coordinates in WGS84
#data_gdf.set_crs(epsg=32618)

#%%

""" EXPORTING DATA TO DBMS """
"""------------------------"""
# setup db connection (generic connection path to be update with your credentials:

engine = create_engine('postgresql://postgres:postgres@localhost:5432/se4g')

# data_df.to_sql('BRWC water quality monitoring', engine, if_exists = 'replace', index=False)

data_gdf.to_postgis('PRWC', engine, if_exists = 'replace', index=False)

#%%

data_clean = gpd.GeoDataFrame.from_postgis('PRWC', engine, geom_col='geometry')
