import flask
from flask import request, jsonify, render_template
import sqlite3

app = flask.Flask(__name__, template_folder='templates')
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Flask App</h1>
<p>A simple flask app to fetch database records of users and create a user record</p>'''


@app.route('/users/all', methods=['GET'])
def users_all():
    conn = sqlite3.connect('crudUsers')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_users = cur.execute('SELECT * FROM users_user;').fetchall()

    return jsonify(all_users)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/users/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('create.html')
    else: # request.method == 'POST':
        # read data from the form and save in variable
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        age = request.form['age']
        address = request.form['address']

        try:
            con = sqlite3.connect('crudUsers')
            c =  con.cursor() 
            
            c.execute("INSERT INTO users_user (firstname, lastname, age, address) VALUES (?,?,?,?)",
                (firstname, lastname, age, address))
            con.commit() 
            return render_template('createdUser.html', firstname=firstname, lastname=lastname, age=age, address=address)
        except con.Error as err: # if error
            # then display the error in page
            return render_template('databaseError.html', error=err)
        finally:
            con.close() # close the connection

@app.route('/users', methods=['GET'])
def users_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    firstname = query_parameters.get('firstname')
    age = query_parameters.get('age')

    query = "SELECT * FROM users_user WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if firstname:
        query += ' firstname=? AND'
        to_filter.append(firstname)
    if age:
        query += ' age=? AND'
        to_filter.append(age)
    if not (id or firstname or age):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('crudUsers')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)

app.run()