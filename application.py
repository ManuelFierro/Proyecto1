import os
from flask import Flask, render_template, redirect, url_for, session, logging, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = "shit"

motor = create_engine(
    "postgres://tybnzuug:sEd-YLwtFP6juILFYUkAKmwTtHpoNasU@drona.db.elephantsql.com:5432/tybnzuug")
db = scoped_session(sessionmaker(bind=motor))

# listar vuelos


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    mensaje = ''
    if request.method == "POST" and 'usuario' in request.form and 'password' in request.form:
        usuario = request.form['usuario']
        password = request.form['password']
        login = db.execute("SELECT * FROM usuarios WHERE usuario = :usuario AND password = :password",
                           {"usuario": usuario, "password": password}).fetchone()

        # If account exists in accounts table in out database
        if login:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['usuario'] = login['usuario']
            # Redirect to home page
            return 'Logged in successfully!'
        else:
            # Account doesnt exist or username/password incorrect
            mensaje = 'Incorrect username/password!'

    return render_template('index.html', mensaje='')


@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    mensaje = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'usuario' in request.form and 'password' in request.form:
        # Create variables for easy access
        usuario = request.form['usuario']
        password = request.form['password']
        db.execute('SELECT * FROM accounts WHERE username = %s', (username))
        cuenta = db.fetchone()
        # If account exists show error and validation checks
        if cuenta:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', usuario):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            db.execute('INSERT INTO accounts VALUES (%s, %s)', (usuario, password))
            db.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        mensaje = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('registro.html', mensaje=mensaje)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('ususario', None)

    # Redirect to login page
    return redirect(url_for('login'))
