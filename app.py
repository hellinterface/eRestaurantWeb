import sqlite3
from flask import Flask, render_template, make_response, request, redirect, Response, abort
import string
import random

sessionKeys = dict(shit="fuck123")

{
    "username": "ajnuagjuaghjuagnh",
    "username2": "gssggsgs",
    "username3": "ajnuagjuaghjgsgsguagnh",
    "username4": "ajnuagjuaghjgsgsgsuagnh",
    "username5": "ajnuagjuaghjgsgsuagnh",
}

def get_db_connection():
    conn = sqlite3.connect('main.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask("eRestaurantWeb")

@app.route('/')
def root():
    userKey = request.cookies.get('sessionkey')
    print(userKey)
    print(sessionKeys.values())
    if userKey not in list(sessionKeys.values()) :
        return redirect('/login')
    currentUsername = ""
    for username, sessionkey in sessionKeys.items():
        if sessionkey == userKey:
            currentUsername = username
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE Username = ' + currentUsername).fetchone()
    entries = conn.execute('SELECT * FROM entries WHERE UsernameID = ' + str(user['ID'])).fetchall()
    conn.close()
    resp = make_response(render_template('entries.html', entries=entries))
    # resp.headers['AuthKey'] = '*'
    return resp


@app.route('/new')
def new():
    userKey = request.cookies.get('sessionkey')
    print(userKey)
    print(sessionKeys.values())
    if userKey not in list(sessionKeys.values()) :
        return redirect('/login')
    conn = get_db_connection()
    tables = conn.execute('SELECT * FROM tables').fetchall()
    cuisines = conn.execute('SELECT * FROM cuisines').fetchall()
    conn.close()
    resp = make_response(render_template('new.html', tables=tables, cuisines=cuisines))
    # resp.headers['AuthKey'] = '*'
    return resp

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        query = 'SELECT * FROM users WHERE Username = "' + request.form['username'] + '" AND Password = "' + request.form['password'] + '"'
        print(query)
        print(request.form['username'], request.form['password'])
        conn = get_db_connection()
        user = conn.execute(query).fetchone()
        conn.close()
        if not user:
            return render_template('login.html', error=True)
        else:
            return authRedirectToMain(request.form['username'])
    if request.method == 'GET':
        return render_template('login.html', error=False)

@app.errorhandler(400)
def page_not_found(error):
    return "INVALID 400"

def generateSessionKey():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

def addSessionKeyForUser(username):
    key = generateSessionKey()
    sessionKeys[username] = key
    return key

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        success = True
        if (len(request.form['username']) < 3): success = False
        if (len(request.form['password']) < 3): success = False
        if (len(request.form['name']) < 3): success = False
        if (len(request.form['surname']) < 3): success = False
        if (success):
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                try: 
                    cur.execute("INSERT INTO Users (Username, Password, Name, Surname) VALUES (?, ?, ?, ?)",
                        (request.form['username'], request.form['password'], request.form['name'], request.form['surname']))
                except:
                    success = False
                conn.commit()
                conn.close()
                print(request.form['username'], request.form['password'])
                
            except IndexError:
                success = False
                
            if (success):
                return authRedirectToMain(request.form['username'])
            else:
                return render_template('signup.html', error=True)
    if request.method == 'GET':
        return render_template('signup.html', error=False)


# @app.route('/auth', methods=('GET'))
def authRedirectToMain(username):
    key = addSessionKeyForUser(username)
    # key = sessionKeys[username]
    # if (not key): return redirect('/login')
    resp = make_response(render_template('auth.html'))
    resp.set_cookie('sessionkey', key)
    return resp, {"Refresh": "1; url=/"}

   # return render_template('edit.html', post=post)


@app.route('/tables', methods=['POST'])
def getAvailableTables():
    request_data = request.get_json()
    
    time_start = None
    time_end = None

    if request_data:
        if 'time_start' in request_data:
            time_start = request_data['time_start']
        else: abort(400)

        if 'time_end' in request_data:
            time_end = request_data['time_end']
        else: abort(400)
    else: abort(400)
    
    query = 'SELECT * FROM entries WHERE (TimeStart NOT BETWEEN {} AND {}) AND (TimeEnd NOT BETWEEN {} AND {})'.format(time_start, time_end, time_start, time_end)
    print(query)
    conn = get_db_connection()
    tables = conn.execute(query).fetchall()
    conn.close()
    parts = list()
    for i in tables:
        parts.append('"id":{}, "seats":{}'.format(i.ID, i.Seats))
    concatenatedTables = ','.join(parts)
    result = '[{}]'.format(concatenatedTables)
    return Response(result, status=200, mimetype='application/json')