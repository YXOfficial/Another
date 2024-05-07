from flask import Flask, request, render_template, redirect, make_response
import requests
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
from flask import url_for
basedir = os.path.abspath(os.path.dirname(__file__))
UploadPath = os.path.join(basedir, app.config['UPLOAD_FOLDER'])


@app.route('/', methods=['POST', 'GET'])
def year():
    Year = ''
    Check = ''
    DisplayCheck = 'none'
    DisplayError = 'none'
    if request.method == 'POST':

        Year = request.form['Year']
        if Year.isnumeric():
            Year = int(Year)
        else:
            DisplayError = 'block'
            return render_template('test.html', Year=Year, Check=Check, DisplayCheck=DisplayCheck,
                               DisplayError=DisplayError)

        if Year % 2 == 0 and Year % 100 != 0:
            Check = "Nhuận"
            DisplayCheck = 'block'
        else:
            Check = "Thường"
            DisplayCheck = 'block'

    return render_template('test.html', Year=Year, Check=Check, DisplayCheck=DisplayCheck, DisplayError=DisplayError)

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    Year = ''
    CheckFile = ''
    DisplayCheck = 'none'
    DisplayErrorFile = 'none'
    if request.method == 'POST':
        f = request.files['file']
        fa = os.path.join(UploadPath, f.filename)
        f.save(fa)
        file_content = open(fa, 'r')


        if file_content:
            Year = file_content.read()
            data ={"Year": Year}
            redirect_response = requests.post('http://127.0.0.1:5000/', data=data).text
            return make_response(redirect_response, 302)
        else:
            DisplayErrorFile = 'block'
            return render_template('upload.html', Year=Year, CheckFile=CheckFile, DisplayCheck=DisplayCheck,
                                  DisplayErrorFile=DisplayErrorFile)

    return render_template('upload.html', Year=Year, CheckFile=CheckFile, DisplayCheck=DisplayCheck, DisplayErrorFile=DisplayErrorFile)

@app.route('/uploaded_file', methods=['POST', 'GET'])
def uploaded():
    dir = os.listdir(UploadPath)
    return render_template('Uploaded.html', dir_list=dir)


app.run(debug=True)