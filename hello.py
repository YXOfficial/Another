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

app.secret_key = '!)@()*)@$*@)@%()%":"::":">">">">">"325faggFF)'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
from flask import url_for
basedir = os.path.abspath(os.path.dirname(__file__))
UploadPath = os.path.join(basedir, app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['POST', 'GET'])
def home():
        if session['loggedin'] == None:
            return redirect('/Login')
        return render_template('Home.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['loggedin'] = None
    session['USERNAME'] = None
    return redirect('/Login')

@app.route('/uploaded_file/<gmail>', methods=['POST', 'GET'])
def uploaded(gmail):
    if not os.path.exists(UploadPath + "/" + gmail):
        os.makedirs(UploadPath + "/" + gmail)
    if request.method == 'POST':
        f = request.files['file']
        filename = f.filename
        filepath = os.path.join(UploadPath + "/" + gmail, filename)
        while os.path.isfile(filepath):
            print("file is duplicated")
            temp = filename.split('.')
            filename = temp[0] + '_copy' + '.' + temp[1]
            filepath = os.path.join(UploadPath + '/' + gmail, filename)


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

    dir = os.listdir(UploadPath + "/" + gmail)
    def gettime(file):
        filepath = os.path.join(UploadPath + "/" + gmail, file)
        return os.path.getctime(filepath)

    dir.sort(key=gettime)

    return render_template('Uploaded.html', dir_list=dir)

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    gmail = session['USERNAME']
    return send_from_directory(UploadPath + '/' + gmail, filename, as_attachment=True)

@app.route('/Login', methods=['GET', 'POST'])
def login():
    if session.get('loggedin') == True:
        return redirect("/")
    message = ''
    if request.method == 'POST' and 'gmail' in request.form and 'password' in request.form:
        gmail = request.form['gmail']
        password = request.form['password']
        cursor.execute('SELECT * FROM LoginInfo WHERE GMAIL = %s AND PASSWORD = %s', (gmail, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['USERNAME'] = account[3]
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
    mydb.commit() ## Refresh MySQL
    cursor.execute('SELECT * FROM logininfo WHERE GMAIL = %s AND TOKEN=%s', (gmail, token))
    counter = cursor.fetchone()
    if not counter:
        return render_template('nope.html')
    else:
        if request.method == 'POST' and 'password' in request.form:
            passchange = request.form['password']
            cursor.execute('UPDATE logininfo SET PASSWORD= %s WHERE GMAIL=%s', (passchange, gmail))
            cursor.execute('UPDATE LoginInfo SET Token=null WHERE GMAIL=%s', (gmail, ))
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
            # cursor.execute('CREATE EVENT DeleteToken ON SCHEDULE EVERY 1 second DO UPDATE LoginInfo SET Token=null WHERE EXPIRY_DATE <= NOW();')
            # Tạo Event Bỏ token khi EXPIRY_DATE nhỏ hơn NOW()


            cursor.execute('UPDATE LoginInfo SET Token = %s, EXPIRY_DATE=current_timestamp() + INTERVAL 30 SECOND WHERE GMAIL = %s', (token, gmail)) ## Expired Time
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