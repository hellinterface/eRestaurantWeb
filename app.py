import sqlite3
from flask import Flask, render_template, make_response, request, redirect, Response, abort
import string
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ключ: имя пользователя
sessionKeys = dict()

# подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('main.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask("eRestaurantWeb")

# страница с перечислением записей
@app.route('/')
def root():
    userKey = request.cookies.get('sessionkey')
    print(userKey)
    print(sessionKeys.values())
    if userKey not in list(sessionKeys.keys()) :
        return redirect('/login')
    currentUsername = sessionKeys[userKey]

    conn = get_db_connection()
    user = conn.execute(f'SELECT * FROM Users WHERE Username = "{currentUsername}"').fetchone()
    entries = ""
    if user['IsAdmin'] == 1:
        entries = conn.execute(f'SELECT * FROM entries').fetchall()
    else:
        entries = conn.execute(f'SELECT * FROM entries WHERE UsernameID = ' + str(user['ID'])).fetchall()
    conn.close()
    namesurname = user['Name'] + " " + user['Surname']
    resp = make_response(render_template('entries.html', namesurname=namesurname, entries=entries))
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
    user = conn.execute(f'SELECT * FROM Users WHERE Username = "{currentUsername}"').fetchone()
    tables = conn.execute('SELECT * FROM tables').fetchall()
    cuisines = conn.execute('SELECT * FROM cuisines').fetchall()
    conn.close()
    namesurname = user['Name'] + " " + user['Surname']
    minDate = (datetime.today() + relativedelta(days=1)).strftime('%Y-%m-%d') # время минимальное
    maxDate = (datetime.today() + relativedelta(days=1) + relativedelta(months=1)).strftime('%Y-%m-%d') # время максимальное (один месяц спустя )
    resp = make_response(render_template('new.html', editEntry=None, namesurname=namesurname, tables=tables, cuisines=cuisines, minDate=minDate, maxDate=maxDate, isAdmin = user['isAdmin']))
    return resp

# вход в аккаунт
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

# генерация ключа сессии
def generateSessionKey():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

# ассоциация ключа сессии и пользователя в словаре sessionKeys
def addSessionKeyForUser(username):
    key = generateSessionKey()
    sessionKeys[key] = username
    return key

# регистрация
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


# дать куки с ключом сессии и перевести пользователя на главную страницу
def authRedirectToMain(username):
    key = addSessionKeyForUser(username)
    # key = sessionKeys[username]
    # if (not key): return redirect('/login')
    resp = make_response(render_template('auth.html'))
    resp.set_cookie('sessionkey', key)
    return resp, {"Refresh": "1; url=/"}

# выход из аккаунта
@app.route('/unauth', methods=['GET'])
def unauth():
    userKey = request.cookies.get('sessionkey')
    if userKey not in list(sessionKeys.keys()) :
        return redirect('/login')
    del sessionKeys[userKey]
    resp = make_response(render_template('auth.html'))
    resp.set_cookie('sessionkey', '')
    return resp, {"Refresh": "1; url=/login"}

# получение доступных столиков
@app.route('/tables', methods=['POST'])
def getAvailableTables():
    request_data = request.get_json()
    
    time_start = None
    time_end = None
    people_count = None

    if request_data:
        if 'time_start' in request_data:
            time_start = request_data['time_start']
        else: abort(400)

        if 'time_end' in request_data:
            time_end = request_data['time_end']
        else: abort(400)

        if 'people_count' in request_data:
            people_count = request_data['people_count']
        else: abort(400)
    else: abort(400)

    tableIDs = list()
    query = 'SELECT * FROM entries WHERE ((TimeStart BETWEEN {} AND {}) OR (TimeEnd BETWEEN {} AND {}))'.format(time_start, time_end, time_start, time_end)
    print(query)
    conn = get_db_connection()
    tables = conn.execute('SELECT * FROM tables WHERE Seats >= {}'.format(people_count)).fetchall()
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

# удаление записи с указанным айди
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
    user = conn.execute(f'SELECT * FROM Users WHERE Username = "{currentUsername}"').fetchone()
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

# занесение изменений в базу данных
@app.route('/apply', methods=['POST'])
def apply():
    success = True
    request_data = request.get_json()
    time_start = None
    time_end = None
    people_count = None
    table_id = None
    cuisine_ids = None
    id = None
    for_username = None

    if request_data:
        if 'time_start' in request_data:
            time_start = request_data['time_start']
        else: abort(400)

        if 'time_end' in request_data:
            time_end = request_data['time_end']
        else: abort(400)

        if 'people_count' in request_data:
            people_count = request_data['people_count']
        else: abort(400)

        if 'table_id' in request_data:
            table_id = request_data['table_id']
        else: abort(400)

        if 'cuisine_ids' in request_data:
            cuisine_ids = request_data['cuisine_ids']
        else: abort(400)

        if 'id' in request_data:
            id = request_data['id']

        if 'for_username' in request_data:
            for_username = request_data['for_username']

    else: abort(400)

    userKey = request.cookies.get('sessionkey')
    if userKey not in list(sessionKeys.keys()): success = False
    currentUsername = sessionKeys[userKey]

    conn = get_db_connection()
    cursor = conn.cursor()
    user = ""
    if (for_username == None): user = conn.execute(f'SELECT * FROM Users WHERE Username = "{currentUsername}"').fetchone()
    else: user = conn.execute(f'SELECT * FROM Users WHERE Username = "{for_username}"').fetchone()
    if (user == None): success = False
    else:
        maxid = conn.execute("SELECT MAX(ID) FROM Entries").fetchone()
        maxid = maxid['MAX(ID)']
        print(maxid)
        if (id == None): # СОЗДАНИЕ
            query = f"INSERT INTO Entries VALUES ({maxid+1}, {user['ID']}, {time_start}, {time_end}, {table_id}, {people_count}, '{cuisine_ids}')"
        else: # ИЗМЕНЕНИЕ
            query = f"UPDATE Entries SET TimeStart = {time_start}, TimeEnd = {time_end}, TableID = {table_id}, PeopleCount = {people_count}, CuisineIDs = '{cuisine_ids}' WHERE ID = {id}"
        #cursor.execute(query)

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

# редактирование записи (открывает страницу создания новой с заполненными полями)
@app.route('/edit', methods=['GET'])
def edit():
    targetID = request.args.get('entryID')
    print(targetID)
    
    userKey = request.cookies.get('sessionkey')
    if userKey not in list(sessionKeys.keys()) :
        return redirect('/login')
    currentUsername = sessionKeys[userKey]

    conn = get_db_connection()
    # cur = conn.cursor()
    # entryExists = cur.execute('SELECT EXISTS(SELECT 1 FROM Entries WHERE ID = {})'.format(targetID)).fetchone()
    # print(entryExists)
    user = conn.execute(f'SELECT * FROM Users WHERE Username = "{currentUsername}"').fetchone()
    if user['IsAdmin'] == 1:
        query = 'SELECT * FROM Entries WHERE ID = {}'.format(targetID)
    else:
        query = 'SELECT * FROM Entries WHERE ID = {} AND UsernameID = {}'.format(targetID, user['ID'])
    print('------------------------------------------')
    print(user['IsAdmin'])
    print('------------------------------------------')
    editEntry = conn.execute(query).fetchone()
    tables = conn.execute('SELECT * FROM tables').fetchall()
    cuisines = conn.execute('SELECT * FROM cuisines').fetchall()
    conn.close()
    namesurname = user['Name'] + " " + user['Surname']
    print(editEntry['TableID'])
    resp = make_response(render_template('new.html', namesurname=namesurname, editEntry=editEntry, cuisines=cuisines, tables=tables, isAdmin = user['IsAdmin']))
    return resp