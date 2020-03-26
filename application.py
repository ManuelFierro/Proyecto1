from flask import Flask, render_template, url_for, session, request, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import date


app = Flask(__name__)
app.secret_key = "shit"

motor = create_engine(
    'postgres://tybnzuug:sEd-YLwtFP6juILFYUkAKmwTtHpoNasU@drona.db.elephantsql.com:5432/tybnzuug', pool_size=20, max_overflow=0)
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
        db.close()
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
        db.close()
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
            db.close()
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
        resenas = db.execute("SELECT titulo,resena,rating FROM resenas INNER JOIN libros ON libros.isbn=resenas.isbn WHERE usuario= :usuario",
                             {"usuario": cuenta}).fetchall()

        db.close()
        if request.args.get('mensaje'):
            mensaje = request.args['mensaje']
        else:
            mensaje = ''
        # muestra la informacion del usuario en el perfil.
        return render_template('perfil.html', resenas=resenas, mensaje=mensaje)
    msg = 'Para entrar al perfil debes estar logeado'
    # User is not loggedin redirect to login page
    return redirect(url_for('index', msg=msg))


@app.route('/busqueda/', methods=['GET', 'POST'])
def busqueda():
    titulo = request.form['busqueda'] + '%'
    #
    # verifica si esta activo el login
    if 'logeado' in session:
        # resultado = db.execute("SELECT usuario FROM usuarios WHERE usuario LIKE :titulo", {"titulo": titulo}).fetchone()
        resultado = db.execute(
            "SELECT titulo,isbn,autor,year FROM libros WHERE titulo LIKE :titulo", {"titulo": titulo}).fetchall()
        db.close()
        if not resultado:
            mensaje = 'Lo sentimos no tenemos ese libro'
            return render_template('libros.html', mensaje=mensaje)
        else:
            mensaje = resultado
            return render_template('libros.html', mensaje=mensaje, libros=resultado)
    mensaje = 'Para usar esta funcion debes estar logeado'
    # User is not loggedin redirect to login page
    return redirect(url_for('index', mensaje=mensaje))


@app.route("/libro/<string:isbn>", methods=['GET', 'POST'])
def libro(isbn):

    # verifica si esta activo el login
    if 'logeado' in session:
        # resultado = db.execute("SELECT usuario FROM usuarios WHERE usuario LIKE :titulo", {"titulo": titulo}).fetchone()
        libro = db.execute("SELECT titulo,isbn,autor,year FROM libros WHERE isbn = :isbn", {
            "isbn": isbn}).fetchone()
        resenas = db.execute("SELECT usuario,resena,isbn,rating FROM resenas WHERE isbn= :isbn",
                             {"isbn": isbn}).fetchall()
        db.close()
        mensaje = 'Informacion del libro:'
        return render_template('libro.html', mensaje=mensaje, libro=libro, resenas=resenas)
    mensaje = 'Para usar estar funcion debes estar logeado'
    # User is not loggedin redirect to login page
    return redirect(url_for('index', mensaje=mensaje))


@app.route("/sidebar/<string:letras>", methods=['GET', 'POST'])
def sidebar(letras):
    titulo = list(letras)

    # verifica si esta activo el login
    if 'logeado' in session:
        # resultado = db.execute("SELECT usuario FROM usuarios WHERE usuario LIKE :titulo", {"titulo": titulo}).fetchone()
        resultadoA = db.execute("SELECT titulo,isbn,autor,year FROM libros WHERE titulo LIKE :letra ORDER BY titulo ASC", {
                                "letra": titulo[0] + '%'}).fetchall()
        resultadoB = db.execute("SELECT titulo,isbn,autor,year FROM libros WHERE titulo LIKE :letra ORDER BY titulo ASC", {
                                "letra": titulo[1] + '%'}).fetchall()
        resultadoC = db.execute("SELECT titulo,isbn,autor,year FROM libros WHERE titulo LIKE :letra ORDER BY titulo ASC", {
                                "letra": titulo[2] + '%'}).fetchall()
        resultadoD = db.execute("SELECT titulo,isbn,autor,year FROM libros WHERE titulo LIKE :letra ORDER BY titulo ASC", {
                                "letra": titulo[3] + '%'}).fetchall()
        db.close()
        mensaje = 'Los libros encontrados son:'
        return render_template('libros.html', mensaje=mensaje, libros1=resultadoA, titulo=titulo, libros2=resultadoB, libros3=resultadoC, libros4=resultadoD)
    mensaje = 'Para entrar al perfil debes estar logeado'
    # User is not loggedin redirect to login page
    return redirect(url_for('index', mensaje=mensaje))


@app.route('/resena/<string:ISBN>', methods=['GET', 'POST'])
def resena(ISBN):
    # variable mensaje para mandar mensajes...
    mensaje = ''

    cuenta = session['usuario']
    libro = db.execute("SELECT titulo,isbn,autor,year FROM libros WHERE isbn = :isbn", {
        "isbn": ISBN}).fetchone()
    # verifica si esta activo el login
    if request.method == 'POST' and 'resena' in request.form and 'rating' in request.form:
        resena = resena = request.form.get("resena")
        rating = request.form.get("rating")

        db.execute("INSERT INTO resenas (usuario,isbn,resena,rating) VALUES (:usuario,:ISBN, :resena, :rating)",
                   {"resena": resena, "ISBN": ISBN, "usuario": cuenta, "rating": rating})
        db.commit()
        db.close()
        mensaje = 'Se agregó una nueva reseña'
        # muestra la informacion del usuario en el perfil.
        return redirect(url_for('perfil', mensaje=mensaje))
    else:
        error = "No se pudo enviar la reseña"
        return render_template('libro.html', error=error, libro=libro)


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
