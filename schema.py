# -*- coding: utf-8 -*-
"""
Created on Sat May 28 14:06:47 2022

@author: Group7
"""

import json
import requests
import pandas as pd
from psycopg2 import connect
from sqlalchemy import create_engine


cleanup = (
        'DROP TABLE IF EXISTS sys_table CASCADE',
        'DROP TABLE IF EXISTS comment_table',
        'DROP TABLE IF EXISTS data_table',
        'DROP TABLE IF EXISTS contact',
        'DROP TABLE IF EXISTS post'
        )

commands =(
        """
        CREATE TABLE sys_table (
            userid SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255)
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
        ,
        """ 
        CREATE TABLE post (
                post_id SERIAL PRIMARY KEY,
                author_id INTEGER NOT NULL,
                created TIMESTAMP DEFAULT NOW(),
                title VARCHAR(350) NOT NULL,
                body VARCHAR(500) NOT NULL,
                FOREIGN KEY (author_id)
                    REFERENCES sys_table (userid)
        )
        """
        )

sqlCommands = (
        'INSERT INTO sys_table (username, password, email) VALUES (%s, %s, %s) RETURNING userid',
        'INSERT INTO post (title, body, author_id) VALUES (%s, %s, %s)'
        )

conn = connect("dbname=SE4GI user=postgres password=postgres")
cur = conn.cursor()
for command in cleanup :
    cur.execute(command)
for command in commands :
    cur.execute(command)
    print('execute command')

cur.execute(sqlCommands[0], ('Giuseppe', '3ety3e7', 'user@admin.com'))
userId = cur.fetchone()[0]
cur.execute(sqlCommands[1], ('My First Post', 'This is the post body', userId))
cur.execute('SELECT * FROM post')
print(cur.fetchall())


cur.close()
conn.commit()
conn.close()




engine = create_engine('postgresql://postgres:postgres@localhost:5432/SE4GI')
