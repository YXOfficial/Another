from flask import Flask, request, render_template, send_from_directory, url_for, session, redirect
from flask_mail import Mail, Message
import re
import os
from werkzeug.utils import secure_filename
import mysql.connector
import random

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Khoa12345@",
  database='logininfo'
)

cursor = mydb.cursor()


app = Flask(__name__)

mail = Mail(app)

# configuration of mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'dashdashgame@gmail.com'
app.config['MAIL_PASSWORD'] = 'hmcwdwtehadifqiu'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
from flask import url_for
basedir = os.path.abspath(os.path.dirname(__file__))
UploadPath = os.path.join(basedir, app.config['UPLOAD_FOLDER'])



@app.route('/uploaded_file', methods=['POST', 'GET'])
def uploaded():
    if request.method == 'POST':
        f = request.files['file']
        filename = f.filename
        filepath = os.path.join(UploadPath, filename)
        while os.path.isfile(filepath):
            print("file is duplicated")
            temp = filename.split('.')
            filename = temp[0] + '_copy' + '.' + temp[1]
            filepath = os.path.join(UploadPath, filename)


        # if os.path.isfile(os.path.join(UploadPath, f.filename)):
        #     print("file is duplicated")
        #     Split = f.filename.split('.')
        #     Split[0] = Split[0]+'copy'
        #     I = Split[0]
        #     Renamed = '.'.join(Split)
        #     while os.path.isfile(os.path.join(UploadPath, Renamed)):
        #         print("duplicated with looping")
        #         Split = Renamed.split('.')
        #         Split[0] = Split[0] + 'copy'
        #         I = Split[0]
        #         Renamed = '.'.join(Split)
        #
        #     fa = os.path.join(UploadPath, Renamed)
        f.save(filepath)

    dir = os.listdir(UploadPath)
    def gettime(file):
        filepath = os.path.join(UploadPath, file)
        return os.path.getctime(filepath)

    dir.sort(key=gettime)

    return render_template('Uploaded.html', dir_list=dir)

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(UploadPath, filename, as_attachment=True)

@app.route('/Login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'gmail' in request.form and 'password' in request.form:
        gmail = request.form['gmail']
        password = request.form['password']
        cursor.execute('SELECT * FROM LoginInfo WHERE GMAIL = %s AND PASSWORD = %s', (gmail, password, ))
        account = cursor.fetchone()
        if account:
            # session['loggedin'] = True
            # session['id'] = account['id']
            # session['USERNAME'] = account['USERNAME']
            message = 'Logged in successfully !'
            return render_template('Login.html', message=message)
        else:
            message = 'Incorrect user and pass'

    return render_template('Login.html', message=message)

@app.route('/Register', methods=['GET', 'POST'])
def Register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        name = request.form['username']
        password = request.form['password']
        gmail = request.form['gmail']

        cursor.execute('SELECT * FROM logininfo WHERE GMAIL = %s', (gmail, ))
        account = cursor.fetchone()
        if account:
            message = "gmail account already exists."
            return render_template('Register.html', message=message)
        else:
            cursor.execute('INSERT INTO LoginInfo (USERNAME, PASSWORD, GMAIL) VALUES (%s, %s, %s)', (name, password, gmail, ))
            mydb.commit()
            message = "Created account."
    return render_template('Register.html', message=message)

@app.route('/PasswordReset/<token>/<gmail>', methods=['GET', 'POST'])
def PasswordChanger(token, gmail):
    message = ''
    cursor.execute('USE logininfo;')
    cursor.execute('SELECT * FROM logininfo WHERE GMAIL = %s AND TOKEN=%s', (gmail, token))
    counter = cursor.fetchone()
    if not counter:
        return render_template('nope.html')
    if request.method == 'POST' and 'password' in request.form:
        passchange = request.form['password']
        cursor.execute('UPDATE logininfo SET PASSWORD= %s WHERE GMAIL=%s', (passchange, gmail))
        mydb.commit()
        message = "changed pass"
    return render_template('Passwordreset.html', message=message, token=token, gmail=gmail)

@app.route('/Reset', methods=['GET', 'POST'])
def Reset():
    message = ''
    if request.method == "POST":
        gmail = request.form['gmail']
        cursor.execute('USE logininfo;')
        cursor.execute('SELECT * FROM logininfo WHERE GMAIL = %s', (gmail,))
        account = cursor.fetchone()
        if not account:
            message = "Not exists."
            return render_template('Reset.html', message=message)
        else:
            token = random.randrange(1, 9999)
            cursor.execute('UPDATE LoginInfo SET Token = %s WHERE GMAIL = %s', (token, gmail))
            mydb.commit()
            msg = Message(
                'Your token, please dont share anyone',
                sender='noreply@gmail.com',
                recipients=[gmail]
            )
            msg.body = ('http://127.0.0.1:5000/PasswordReset/{0}/{1}'.format(token, gmail))
            mail.send(msg)
            message = 'sent'
    return render_template('Reset.html', message=message)


app.run(debug=True)