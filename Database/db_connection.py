# -*- coding: utf-8 -*-
"""
Created on Fri May 20 02:54:27 2022

@author: A.Mukhtar
"""

# import packages
import json
import requests
import numpy as np
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine

"""DATABASE"""
# Function "Update_WQM_DB" loads the raw data from the Epicollect5 API ,process it and cleans it to send it to the
# local server database management system postgreSQL

def Update_WQM_DB():
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

    """ DATA CLEANING """
    """---------------"""
    # Remove unuseful data 
    data_df = whole_df.drop(['ec5_uuid','created_at','uploaded_at','1_Samplers_First_Nam','16_Upstream_photo','17_Downstream_photo','18_Which_method_did_','21_Which_method_did_'], axis = 1)
    # rename All Columns in the dataset //df.set_axis (['new_col1', 'new_col2', 'new_col3', 'new_col4'], axis='columns')//
    data_df = data_df.set_axis(['Title', 'Location_site', 'Sample_Type', 'Date', 'Time', 'Nearest_USGS', 'Streamflow_cfs', 'Sample"wet/dry"', 'Weather_c', 'Airtemp_C', 'Water_level', 'Water_odor', 'Water_color', 'Observed_use', 'Watertemp_C', 'Conductivity_Scm', 'Obs/Comments', 'Bacteria_Lvl(MPN/100ml)', 'Nitrate(mg/L)', 'latitude', 'longitude', 'accuracy', 'UTM_Northing', 'UTM_Easting', 'UTM_Zone'], axis='columns')
    # a back-up database is stored in a csv file
    data_df.to_csv(r'.../BRWC_db.txt')

    # creating new columns with numeric coordinate and accuracy values
    data_df['latitude'] = pd.to_numeric(data_df['latitude'], errors='coerce')
    data_df['longitude'] = pd.to_numeric(data_df['longitude'], errors='coerce')
    data_df['accuracy'] = pd.to_numeric(data_df['accuracy'], errors='coerce')

    # from Pandas DataFrame to GeoPandas GeoDataFrame
    data_gdf = gpd.GeoDataFrame(data_df, geometry=gpd.points_from_xy(data_df.longitude, data_df.latitude))
    # setting up the reference system for the geodesic coordinates in WGS84
    data_gdf= data_gdf.set_crs(epsg=4326, inplace=True)


    """ EXPORTING DATA TO DBMS """
    """------------------------"""
    # setup db connection (generic connection path to be update with your credentials:
    #'postgresql://user:password@localhost:5432/database name')
    engine = create_engine('postgresql://postgres:Blue_sky7@localhost:5432/SE4G')

    #data_df.to_sql('BRWC_water_-quality_monitoring', engine, if_exists = 'replace', index=False)
    data_gdf.to_postgis('water_quality_monitoring', engine, if_exists = 'replace', index=False)
    return

# Function to load the database from PostgreSQL
def Load_gdf_WQM_DB():
    """ REQUEST DATA FROM SERVER SE4GI """
    """--------------------------------"""
    DBfile = open('Database/dbConfig.txt')
    connection = DBfile.readline()
    engine = create_engine(connection)
    # read the geodataframe from a postgreSQL table
    data_geodf = gpd.read_postgis('water_quality_monitoring', engine, geom_col='geometry')
    return data_geodf



