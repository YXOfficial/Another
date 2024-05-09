from flask import Flask, request, render_template, make_response, send_from_directory
import requests
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
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

app.run(debug=True)