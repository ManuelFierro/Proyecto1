from flask import Flask, render_template, url_for, session, request, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
app = Flask(__name__)
app.secret_key = "shit"

motor = create_engine(
    'postgres://tybnzuug:sEd-YLwtFP6juILFYUkAKmwTtHpoNasU@drona.db.elephantsql.com:5432/tybnzuug')
db = scoped_session(sessionmaker(bind=motor))


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    mensaje = ''
    sesion = ''
    if request.method == "POST" and 'usuario' in request.form and 'password' in request.form:
        usuario = request.form['usuario']
        password = request.form['password']
        cuenta = db.execute('SELECT * FROM usuarios WHERE usuario= :usuario AND password= :password',
                            {"usuario": usuario, "password": password}).fetchone()

        # si la cuenta existe en la base de datos y concuerda la pass
        if cuenta:
            # crea sesion con el nombre de usuario
            session['logeado'] = True
            session['usuario'] = cuenta['usuario']
            session['password'] = cuenta['password']
            # si todo salio bien redirecciona a pagina de perfil
            return redirect(url_for('perfil'))
        else:
            # si la los datos no coninciden..
            mensaje = '¡Verifique sus datos!'

    return render_template('index.html', mensaje=mensaje, sesion=sesion)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    # variable mensaje para mandar mensajes...
    mensaje = ''
    # verifica si el usuario y password del form existen o no en la bd
    if request.method == 'POST' and 'usuario' in request.form and 'password' in request.form:
        # crea variables de usuario y password para facilitar la consulta
        usuario = request.form['usuario']
        password = request.form['password']
        account = db.execute("SELECT * FROM usuarios WHERE usuario= :usuario",
                             {"usuario": usuario}).fetchone()
        # verifica si la cuenta existe, se agrega el mensaje acorde
        if account:
            mensaje = '¡Ya existe una cuenta con ese usuario!'
        elif not usuario or not password:
            mensaje = '¡Por favor rellene los campos!'
        else:
            # si la cuenta no existe y los datos son validos se ingresaran los datos en la bd
            db.execute("INSERT INTO usuarios (usuario,password) VALUES (:usuario, :password)",
                       {"usuario": usuario, "password": password})
            db.commit()
            mensaje = 'Se registro con exito!'
            return redirect(url_for('login'))
    elif request.method == 'POST':
        # si el formulario esta vacio muestre mensaje
        mensaje = '¡Por favor rellene los campos!'

    return render_template('registro.html', mensaje=mensaje)


@app.route('/home')
def home():
    # comprueba si esta activo el login
    if 'logeado' in session:
        cuenta = session['usuario']

        # si el usuario esta logeado abrir pagina principal o home
        return render_template('home.html', cuenta=cuenta)

    # si no lo esta redireccionar al login
    return redirect(url_for('login'))


@app.route('/perfil')
def perfil():
    # verifica si esta activo el login
    if 'logeado' in session:
        # query para obtener todos los datos del usuario
        # datos = db.execute('SELECT * FROM usuarios WHERE usuario= :usuario',
        # {"usuario": session['usuario']}).fetchone()
        cuenta = session['usuario']
        # muestra la informacion del usuario en el perfil.
        return render_template('perfil.html', cuenta=cuenta)

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    # limpia los datos del session
    session.pop('logeado', None)
    session.pop('ususario', None)

    # redirecciona al login
    return redirect(url_for('login'))
