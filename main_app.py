# -*- coding: utf-8 -*-
"""
Created on Tue May 31 17:17:43 2022

@author: Huzaifa
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, g

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from psycopg2 import connect

# Create the application instance
app = Flask(__name__,template_folder='templates')
app.secret_key = '!@3QWeASdZXc'


#This function creates a connection to the database saved in Database.txt
def conn_db():
    if 'db' not in g:
        
        g.db =  connect("dbname=SE4G user=postgres password=Blue_sky7")
    
    return g.db

def enddb_conn():
    if 'db' in g:
        g.db.close()
        g.pop('db')


# Create a URL route in our application for "/" and other html pages
@app.route('/')
def start():
     return render_template('start.html')
 
@app.route('/Signup', methods=('GET', 'POST'))
@app.route('/signup', methods=('GET', 'POST'))
def signup():
     if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email    = request.form['email']
        error    = None

        if not username:
            error = 'Please fill out this field.'
        elif not password:
            error = 'Please fill out this field.'
        else :
            conn = conn_db()
            cur = conn.cursor()
            cur.execute('SELECT userid FROM sys_table WHERE username = %s', (username,))
            if cur.fetchone() is not None:
                error = 'Username already used! try another one please!'
                cur.close()

        if error is None:
            conn = conn_db()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO sys_table (username, password, email) VALUES (%s, %s,%s)',
                (username, generate_password_hash(password), email))
            cur.close()
            conn.commit()
            return redirect(url_for('login'))

        flash(error)
    
     return render_template('signup.html')

 
@app.route('/Login', methods=('GET', 'POST'))
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        conn = conn_db()
        cur = conn.cursor()
        error = None
        cur.execute('SELECT * FROM sys_table WHERE username = %s', (username,))
        
        
        sys = cur.fetchone()
        cur.close()
        conn.commit()
        
       
        if sys is None:
            error = 'Login failed! Wrong Username!'
        elif not check_password_hash(sys[2], password):
            error = 'Login failed! Wrong Password!'
            
        if error is None:
            session.clear()
            session['userid'] = sys[0]
            return render_template('home.html')
        
        flash(error)
        
    return render_template('login.html')
 
@app.route('/home')
def home():
     return render_template('home.html')
 

@app.route('/generic')
def generic():
     return render_template('generic.html')

@app.route('/elements')
def elements():
     return render_template('elements.html')

@app.route('/about_us')
def about_us():
     return render_template('about_us.html')
 
@app.route('/contact')
def contact():
    return render_template('contact.html')

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
 app.run(debug=True)