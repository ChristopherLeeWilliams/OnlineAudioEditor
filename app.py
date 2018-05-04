from flask import Flask, render_template, url_for, redirect, request, Response, jsonify
from flask_bootstrap import Bootstrap
from PIL import Image
from werkzeug.utils import secure_filename
import os
import io
import base64
import pydub
from pydub import AudioSegment

app= Flask(__name__, static_url_path = "/static", static_folder = "static")
bootstrap = Bootstrap(app)


# CURRENT ROUTE WHERE FILE DATA IS SENT
@app.route('/test', methods=['POST','GET'])
def test_audio():
    # Currently fixed on mp3 uploads (just for simplicity)

    # Parse JSON Data From Request
    json_data = request.json

    # Get content type
    # Example: "audio/mp3" (we can use this later to filter operations based on audio type)
    contentType = json_data['contentType']

    # B64 data with ascii encoding (audio data)
    base64_data = json_data['base64']

    # Decode b64 ascii data to get bytes (a file-like object)
    byte_data = base64.b64decode(base64_data)

    # Open song in pydub via a bytestream
    # This is our song object now which we can manipulate in pydub
    song = AudioSegment.from_file(io.BytesIO(byte_data), format="mp3")

    # Example song manipulation (only get last 5 seconds)
    return_song = song[-5000:]

    # Export modified audio file to a bytes object (through a bytestream)
    f = io.BytesIO()
    f = return_song.export(f, format='mp3')
    f.seek(0)
    new_song_data = f.read() # Bytes of modified song

    # b64 ascii encode the bytes to be sent back to the client
    # This part can also be modified to just send the file as a download to the client
    b64_formatted_new_song = base64.b64encode(new_song_data).decode('ascii')
    return jsonify(b64_formatted_new_song)


@app.route('/crop', methods=['POST'])
def crop_audio():
    return "audio cropped"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    return render_template('index.html')

# @app.route('/download' methods=['POST'])
# def download_file():
