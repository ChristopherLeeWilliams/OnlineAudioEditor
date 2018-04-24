from flask import Flask, render_template, url_for, redirect, request, Response
from flask_bootstrap import Bootstrap
from PIL import Image
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['mp3','m4a'])

app= Flask(__name__, static_url_path = "/static", static_folder = "static")
bootstrap = Bootstrap(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_file(file):
    return file.read()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            return render_template('uploaded_file.html', file=str(file.mimetype))
    return render_template('index.html')
