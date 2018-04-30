from flask import Flask, render_template, url_for, redirect, request, Response, jsonify
from flask_bootstrap import Bootstrap
from PIL import Image
from werkzeug.utils import secure_filename
import os
import base64

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['mp3','m4a'])

app= Flask(__name__, static_url_path = "/static", static_folder = "static")
bootstrap = Bootstrap(app)


# CURRENT ROUTE WHERE FILE DATA IS SENT
@app.route('/test', methods=['POST','GET'])
def test_audio():
    jsonData = request.get_json()

    # THIS IS THE AUDIO BYTE DATA (The File)
    decoded = base64.b64decode(jsonData['data'])

    # Print to console the audio byte data
    print(decoded)

    # For now return the unmodified base64 string data sent up
    return jsonify(jsonData['data'])
    # return jsonify("Got Data")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    return render_template('index.html')
