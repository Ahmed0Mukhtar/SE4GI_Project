# Group 7 project - Recomendations to run our software without any problem

--BEFORE RUNNING THE SOFTWARE--
1 - PgAdmin should be installed on your computer :
        Open PgAdmin, and create a new database. Add Postgis extention in it.

2 - Python 3.9 should be installed in your environment, together with the following packages :
            geopandas,
            geopy,
            descartes,
            seaborn,
            contextily,
            requests,
            folium,
            flask,
            bokeh,
            git,
            geoalchemy2.
            
3 - From github, download the wole SE4GI_project repository on your device.

4 - In the file preprocessing.py, modify the line 86, putting your actual username, password and database name for accessing your Postgres Database instead of the ones already written. Then run it.

5 - Run the schema.py, after changing the username, password, and database name lines 60 and 82.
      
6 - Now everything is done ! You can run the file main_app.py and go see it on your localhost !!

