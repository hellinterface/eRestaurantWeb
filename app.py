import sqlite3
from flask import Flask, render_template, make_response, request, redirect, Response, abort
import string
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ключ: имя пользователя
sessionKeys = dict()

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
    if userKey not in list(sessionKeys.keys()) :
        return redirect('/login')
    currentUsername = sessionKeys[userKey]

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Users WHERE Username = ' + currentUsername).fetchone()
    entries = conn.execute('SELECT * FROM entries WHERE UsernameID = ' + str(user['ID'])).fetchall()
    conn.close()
    namesurname = user['Name'] + " " + user['Surname']
    resp = make_response(render_template('entries.html', namesurname=namesurname, entries=entries))
    # resp.headers['AuthKey'] = '*'
    return resp


@app.route('/new')
def new():
    userKey = request.cookies.get('sessionkey')
    print(userKey)
    print(sessionKeys.values())
    if userKey not in list(sessionKeys.keys()) :
        return redirect('/login')
    currentUsername = sessionKeys[userKey]

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Users WHERE Username = ' + currentUsername).fetchone()
    tables = conn.execute('SELECT * FROM tables').fetchall()
    cuisines = conn.execute('SELECT * FROM cuisines').fetchall()
    conn.close()
    namesurname = user['Name'] + " " + user['Surname']
    minDate = datetime.today().strftime('%Y-%m-%d')
    maxDate = (datetime.today() + relativedelta(months=1)).strftime('%Y-%m-%d')
    resp = make_response(render_template('new.html', namesurname=namesurname, tables=tables, cuisines=cuisines, minDate=minDate, maxDate=maxDate))
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
    sessionKeys[key] = username
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

    tableIDs = list()
    query = 'SELECT * FROM entries WHERE ((TimeStart BETWEEN {} AND {}) OR (TimeEnd BETWEEN {} AND {}))'.format(time_start, time_end, time_start, time_end)
    print(query)
    conn = get_db_connection()
    tables = conn.execute('SELECT * FROM tables').fetchall()
    entries = conn.execute(query).fetchall()
    conn.close()
    print(entries)
    for i in list(tables):
        tableIDs.append(i["ID"])
    for i in list(entries):
        tableIDs.remove(i["TableID"])
    print(tableIDs)
    concatenatedTables = ','.join(map(str, tableIDs))
    result = '[{}]'.format(concatenatedTables)
    return Response(result, status=200, mimetype='application/json')


# POST: <ID-номер>
@app.route('/delete', methods=['POST'])
def delete():
    success = True

    request_data = request.get_data()
    if not request_data: success = False
    targetID = int(request_data)

    userKey = request.cookies.get('sessionkey')
    if userKey not in list(sessionKeys.keys()): success = False
    currentUsername = sessionKeys[userKey]

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM Users WHERE Username = ' + currentUsername).fetchone()
    if user['IsAdmin'] == 1:
        query = 'DELETE FROM Entries WHERE ID = {}'.format(targetID)
    else:
        query = 'DELETE FROM Entries WHERE ID = {} AND UsernameID = {}'.format(targetID, user['ID'])

    try:
        conn.execute(query)
        conn.commit()
        success = True
    except IndexError:
        success = False
    conn.close()

    if (success):
        return Response('{"success": true}', status=200, mimetype='application/json')
    else:
        return Response('{"success": false}', status=400, mimetype='application/json')