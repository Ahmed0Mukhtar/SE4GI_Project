# -*- coding: utf-8 -*-
"""
@author: Group7
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, g

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from psycopg2 import connect

# Create the application instance
app = Flask(__name__,template_folder='templates')
app.secret_key = 'Huzaifamkk14'

#This function creates a connection to the database saved in Database.txt

def conn_db():
    if 'db' not in g:
        
        g.db =  connect("dbname=se4g user=postgres password=Huzaifamkk14")
    
    return g.db

def enddb_conn():
    if 'db' in g:
        g.db.close()
        g.pop('db')

# Create a URL route in our application for "/" and other html pages
 
@app.route('/Signup', methods=('GET', 'POST'))
@app.route('/signup', methods=('GET', 'POST'))
def signup():
     if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email    = request.form['email']
        error    = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email: 
            error = 'email is required.'
        else :
            conn = conn_db()
            cur = conn.cursor()
            
            cur.execute('SELECT userid FROM sys_table WHERE username = %s', (username,))
            check_username = cur.fetchone()
            
            cur.execute('SELECT userid FROM sys_table WHERE email = %s', (email,))
            check_email = cur.fetchone()
            
            if check_username is not None:
                error = 'Username {} already exists. try another one!'.format(username)
                cur.close()
                
            elif check_email is not None:
                error = 'The email already exists.'
                cur.close()
                conn.close()

        if error is None:
            cur.execute(
                'INSERT INTO sys_table (username, password, email) VALUES (%s, %s,%s)',
                (username, generate_password_hash(password), email))
            cur.close()
            conn.commit()
            conn.close()
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
        conn.close()
       
        if sys is None:
            error = 'Incorrect username.'
        elif not check_password_hash(sys[2], password):
            error = 'Incorrect password.'
            
        if error is None:
            session.clear()
            session['userid'] = sys[0]
            return redirect(url_for('home'))
        
        flash(error)
        
    return render_template('login.html')
    
@app.route('/logout')
@app.route('/logout')
def logout():
        session.clear()
        return redirect(url_for('start'))
    
#@app.before_app_request

def load_logged_in_user():
    user_id = session.get('userid')
    
    if user_id is None:
       g.user = None
       
    else:
       conn =  connect("dbname=se4g user=postgres password=Huzaifamkk14")
       cur = conn.cursor()
       cur.execute('SELECT * FROM sys_table WHERE userid = %s', (user_id,))
       
       g.user = cur.fetchone()
       cur.close()
       conn.commit()
       
    if g.user is None:
        return False
    else: 
        return True   

# Create a URL route in our application for "/" and other html pages

@app.route('/')
@app.route('/start')
def start():
    return render_template('start.html')

@app.route('/home')
def home():
    conn = conn_db()
    cur = conn.cursor()
    cur.execute(
            """SELECT sys_table.username, post.post_id, post.created, post.title, post.body 
               FROM sys_table, post WHERE  
                    sys_table.userid = post.author_id"""
                    )
    posts = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    load_logged_in_user()
    #%%
    #importing packges for preparing data and plot map

    import geopandas as gpd
    from bokeh.models import ColumnDataSource
    from bokeh.plotting import figure
    from bokeh.tile_providers import CARTODBPOSITRON, get_provider
    from bokeh.layouts import row
    from sqlalchemy import create_engine
    from bokeh.embed import components
    from bokeh.resources import CDN

    # Retrieving dataset from the Database
    engine = create_engine('postgresql://postgres:Huzaifamkk14@localhost:5432/se4g')
    
    data = gpd.GeoDataFrame.from_postgis('PRW', engine, geom_col='geometry').to_crs(3857)
    #data = data.to_crs(3857)
    
    
    # Preparing data dor plotting
    
    data['x'] = data['geometry'].x
    data['y'] = data['geometry'].y
    
    data_map = data.drop('geometry', axis=1)
    
    palette=["#29bbff","#f5ff1a","#ff211a"]
    colormap={i : palette[i] for i in [0,1,2]}
    colors=[colormap[x] for x in data_map.Water_class]
    data_map['colors']=colors
    
    
    #Preparing the figure
    
    #(b,d) = 41.795657, -72.860289
    #(a,c) = 41.6333328,-73.3157797
    #(a,b)_EPSG:3857 = (-8161475.26, -8110770.26), (c,d)_EPSG:3857 = (5106211.74, 5130418.82),
    
    
    TOOLTIPS = [
        ("Reference gauge ", "@Nearest_USGS"),
        ("Bacteria level (MPN/100ml)", "@Bacteria_MPNper100ml"),
        ("Safe for ", "@Safe_uses")
        ]
    
    cds = ColumnDataSource(data_map)
    
    MAP = figure(title='Bacteria Map', 
           width = 700, height = 700,
           x_range = (-8170850.62, -8131888.80), y_range = (5071521.81, 5116146.29),
           x_axis_type="mercator", y_axis_type="mercator", 
           tooltips=TOOLTIPS)
    
    MAP.add_tile(get_provider(CARTODBPOSITRON))
    
    MAP.scatter(x='x', y='y', source=cds, marker="inverted_triangle", line_color='black', fill_color='colors', size = 20)
    script1, div1 = components(MAP)
    cdn_js = CDN.js_files[0]

    return render_template ("home.html", posts=posts, script1=script1, div1=div1, cdn_js = cdn_js)
    #%%

@app.route('/contact', methods=('GET', 'POST'))
def contact():
    if request.method == 'POST':
       name    = request.form['name']
       email   = request.form['email']
       subject = request.form['subject']
       message = request.form['message']
       conn    = conn_db()
       cur     = conn.cursor()
       error   = None
       
       cur.execute('SELECT userid FROM sys_table WHERE email = %s', (email,))
       userid = cur.fetchone()     
       if userid is None:
            error = 'register first to send message!'
            cur.close()
            conn.commit()
            conn.close()
            
       else:
            cur.execute('SELECT userid FROM contact WHERE userid = %s', (userid,))
         
            if cur.fetchone() is not None:
                  error = 'You already sent your message!'
                  cur.close()
                  conn.commit()
                  conn.close()
                  
            else:
                 cur.execute('INSERT INTO contact (userid, name, email,subject, message) VALUES (%s, %s, %s, %s, %s)',
                   (userid, name, email, subject, message))      
                 error = 'Thank you! Your message was sent successfully. We will respond as soon as possible.'
                 cur.close()
                 conn.commit()
                 conn.close()
            
       flash(error)
    return render_template('contact.html')
            
          
@app.route('/generic')
def generic():
     return render_template('generic.html')

@app.route('/about_us')
def about_us():
     return render_template('about_us.html')

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
 app.run(debug=True)
