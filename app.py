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

# --------------------------------------- ROUTES ---------------------------------------

# Notes on crop and splice timestamps
#   Some error checking has been done on client via javascript to help insure:
#   - The startTime passed will never be less than 0
#   - The endTime passed will at max be the song duration
#   - startTime will always be less than endTime
#
#   It may be worth setting up some error catching later for good measure though.
#   (Client side scripts can be modified by determined users)

@app.route('/crop', methods=['POST','GET'])
def crop_audio():
    json_data = request.json

    #return jsonify(something in dictionary format)
    return jsonify({"data":"Song Cropped"})

@app.route('/splice', methods=['POST'])
def splice_audio():
    return "Song Spliced"

# TEST ROUTE: Format should be the same for most other routes
@app.route('/test', methods=['POST','GET'])
def test_audio():
    # Parse JSON Data From Request and convert b64 ascii audio data to pydub song
    json_data = request.json
    pydub_data = b64_ascii_to_pydub(json_data["base64"], json_data["contentType"])
    if("error" in pydub_data):
        return jsonify({ "error": pydub_data["error"] })

    # --------------------------------------------------------
    # AUDIO MANIPULATION HAPPENS HERE
    song = pydub_data["song"]
    # Example song manipulation (only get last 5 seconds)
    return_song = song[-5000:]
    # --------------------------------------------------------

    # Instead of converting back, downloads can be queued here (looking into it)

    # Convert audio data back to b64 ascii to be played on client side
    # Second argumnet of pydub_to_b64_ascii allows for audio conversions
    b64_new_song_data = pydub_to_b64_ascii(return_song, pydub_data["format"])
    return jsonify(b64_new_song_data)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    return render_template('index.html')

# ------------------------------------- END ROUTES -------------------------------------


# ------------------------------------- FUNCTIONS --------------------------------------
def contentType_to_format(cT):
    # Translates contentType supplied from
    #  client to audio format used in pydub
    return {
        'audio/mp3': "mp3",
        'audio/mpeg': "mp3",
        'audio/flac': "flac",
        'audio/wav' : "wav",
        'audio/ogg' : "ogg",
        'audio/m4a' : "m4a"
    }.get(cT, -1)   # If type not found, returns -1

def format_to_contentType(f):
    return {
        'mp3': "audio/mp3",
        'mpeg': "audio/mp3",
        'flac': "audio/flac",
        'wav' : "audio/wav",
        'ogg' : "audio/ogg",
        'm4a' : "audio/m4a"
    }.get(f, "audio/mp3")   # If type not found, default on mp3

def b64_ascii_to_pydub(b64Song=-1, contentType=-1):
    # Converts client supplied b64 ascii audio data with
    #   specified contentType to pydub formatted song

    if((b64Song==-1) or (contentType==-1)):
        return {"error":"Missing audio data from upload"}

    # convert contentType to audio format (Example: "audio/mp3" -> "mp3")
    format = contentType_to_format(contentType)
    if (format == -1):
        return {"error":"file type not supported"}

    # Decode b64 ascii data to get bytes (a file-like object)
    byte_data = base64.b64decode(b64Song)

    # Open song in pydub via a bytestream
    # This is our song object now which we can manipulate in pydub
    song = AudioSegment.from_file(io.BytesIO(byte_data), format=format)

    # Return a dictionary with the song format and the pydub song
    return {
        "format":format,
        "song":song
    }

def pydub_to_b64_ascii(pydubSong, exportFormat):
    # Converts pydub formatted audio to b64 ascii format
    #   for playing on client side audio player
    # AUDIO CONVERSION CAN HAPPEN HERE (exportFormat)

    # May want to set up error catching here (pydub specific)

    # Export modified audio file to a bytes object (through a bytestream)
    f = io.BytesIO()
    f = pydubSong.export(f, format=exportFormat)
    f.seek(0)
    song = f.read() # Bytes of modified song

    # b64 ascii encode the bytes to be sent back to the client
    # This part can also be modified to just send the file as a download to the client
    return {
        "song": base64.b64encode(song).decode('ascii'),
        "contentType": format_to_contentType(exportFormat)
    }


def downloadArtCover(artist, album):
    file_size = int('600')
    file_path = "coer.jpg"
    subprocess.check_call([r"sacad.exe", str(artist), str(album), str(file_size), str(file_path)])



# ----------------------------------- END FUNCTIONS ------------------------------------
