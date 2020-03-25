from flask import Flask, render_template, url_for, session, request, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import date


app = Flask(__name__)
app.secret_key = "shit"

motor = create_engine(
    'postgres://tybnzuug:sEd-YLwtFP6juILFYUkAKmwTtHpoNasU@drona.db.elephantsql.com:5432/tybnzuug')
# 'mysql+mysqldb://waveinc:DANTE8888@waveinc.mysql.pythonanywhere-services.com:3306/waveinc$proyecto1')


db = scoped_session(sessionmaker(bind=motor))


@app.route("/", methods=["GET"])
def index():
    if request.args.get('msg'):
        msg = request.args['msg']
    else:
        msg = ''
    cuenta = ''
    if 'logeado' in session:
        cuenta = session['usuario']
        # muestra la informacion del usuario en el perfil.
        return render_template('index.html', cuenta=cuenta)
    return render_template("index.html", cuenta=cuenta, msg=msg)


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

    return render_template('login.html', mensaje=mensaje, sesion=sesion)


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
        return render_template('index.html', cuenta=cuenta)

    # si no lo esta redireccionar al login
    return redirect(url_for('login'))


@app.route('/perfil', methods=['GET', 'POST'])
def perfil():

    # verifica si esta activo el login
    if 'logeado' in session:
        cuenta = session['usuario']
        resenas = db.execute("SELECT resena,isbn,rating FROM resenas WHERE usuario= :usuario",
                             {"usuario": cuenta}).fetchall()
        if request.args.get('mensaje'):
            mensaje = request.args['mensaje']
        else:
            mensaje = ''
        # muestra la informacion del usuario en el perfil.
        return render_template('perfil.html', resenas=resenas, mensaje=mensaje)
    msg = 'Para entrar al perfil debes estar logeado'
    # User is not loggedin redirect to login page
    return redirect(url_for('index', msg=msg))


@app.route('/resena', methods=['GET', 'POST'])
def resena():
    # variable mensaje para mandar mensajes...
    mensaje = ''
    cuenta = session['usuario']

    # verifica si esta activo el login
    if request.method == 'POST' and 'resena' in request.form and 'rating' in request.form:
        resena = resena = request.form.get("resena")
        rating = request.form.get("rating")
        db.execute("INSERT INTO resenas (usuario,isbn,resena,rating) VALUES (:usuario,1416949658, :resena, :rating)",
                   {"resena": resena, "usuario": cuenta, "rating": rating})
        db.commit()
        mensaje = 'Se agregó una nueva reseña'
        # muestra la informacion del usuario en el perfil.

        return redirect(url_for('perfil', mensaje=mensaje))

    elif request.method == 'POST':
        # si el formulario esta vacio muestre mensaje
        msg = 'no se pudo enviar el mensaje'

    # User is not loggedin redirect to login page
    return redirect(url_for('perfil', msg=msg))


@app.route('/logout')
def logout():
    # limpia los datos del session
    session.pop('logeado', None)
    session.pop('usuario', None)
    session.pop('password', None)

    # redirecciona al login
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug = True
    app.run()
