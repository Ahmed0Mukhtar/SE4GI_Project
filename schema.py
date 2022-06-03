# -*- coding: utf-8 -*-
"""
Created on Sat May 28 14:06:47 2022

@author: A.Mukhtar
"""

import json
import requests
import pandas as pd
from psycopg2 import connect
from sqlalchemy import create_engine


cleanup = (
        'DROP TABLE IF EXISTS sys_table CASCADE',
        'DROP TABLE IF EXISTS comment_table',
        'DROP TABLE IF EXISTS data_table'
        )

commands =(
        """
        CREATE TABLE sys_table (
            userid SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255),
        )
        """
        ,
        """
        CREATE TABLE comment_table (
            comment_id SERIAL PRIMARY KEY,
            userid INTEGER NOT NULL UNIQUE,
            created TIMESTAMP DEFAULT NOW(),
            comment VARCHAR(500) NOT NULL,
            FOREIGN KEY (userid)
                    REFERENCES sys_table (userid)
 
        )
        """
        ,
         """
        CREATE TABLE contact (
            userid INTEGER NOT NULL UNIQUE,
            name VARCHAR(500) NOT NULL,
            email VARCHAR(500) NOT NULL,
            message VARCHAR(500) NOT NULL,
            Guest VARCHAR(500),
            FOREIGN KEY (userid)
                    REFERENCES sys_table (userid)
        )
        """
        
        )

conn = connect("dbname=SE4G user=postgres password=Blue_sky7")
cur = conn.cursor()

for command in cleanup:
    cur.execute(command)
for command in commands:
    cur.execute(command)



cur.close()
conn.commit()
conn.close()




engine = create_engine('postgresql://postgres:Blue_sky7@localhost:5432/SE4G')