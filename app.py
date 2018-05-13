from flask import Flask, render_template, url_for, redirect, request, Response, jsonify, send_file, make_response
from flask_bootstrap import Bootstrap
from PIL import Image
from werkzeug.utils import secure_filename
from pydub import AudioSegment
from PIL import Image
import os, io, base64, pydub, urllib, urllib.request

# SACAD IMPORTS
__requires__ = 'sacad==2.1.1'
import subprocess

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

@app.route('/youtubeDL', methods=['POST','Get'])
def yt_dl():
    json_data = request.json
    outtmpl = newname + '.%(ext)s'
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        },
        {'key': 'FFmpegMetadata'},
        ],

    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(self.urledit.text(), download=True)

@app.route('/crop', methods=['POST','GET'])
def crop_audio():
    json_data = request.json
    pydub_data = b64_ascii_to_pydub(json_data["base64"], json_data["contentType"])
    if("error" in pydub_data):
        return jsonify({ "error": pydub_data["error"] })
    song = pydub_data["song"]
    cropsong = song[json_data["startTime"]:json_data["endTime"]]
    base64_audio = pydub_to_b64_ascii(cropsong, pydub_data["format"])
    #return jsonify(something in dictionary format)
    return jsonify(base64_audio)

@app.route('/downloadAudioWithAlbumArt', methods=['POST'])
def downloadAudioWithAlbumArt():
    json_data = request.json

    # Get image and resize for album art
    image_data = b64_ascii_to_pillow(json_data["base64_image"])
    if("error" in image_data):
        return jsonify({"error":image_data["error"]})
    image = image_data["image"].resize((300,300))

    song = base64.b64decode(json_data["base64_audio"])

    return jsonify({"song":json_data["base64_audio"],"contentType":json_data["contentType_audio"]})

    # return jsonify({"msg":"Added Album Art!"})

@app.route('/getImageData', methods=['POST'])
def get_image_data():
    # Given an image URL, downloads the b64 image data
    json_data = request.json
    img = image_url_to_pillow(json_data["url"])
    if(img == -1):
        return jsonify({"error":"Invalid Url"})

    # img here is editable in pillow
    resized = img.resize((300,300))
    img_b64 = pillow_image_to_b64_ascii(resized)
    return jsonify(img_b64)

@app.route('/splice', methods=['POST'])
def splice_audio():
    json_data = request.json
    pydub_data = b64_ascii_to_pydub(json_data["base64"], json_data["contentType"])
    if("error" in pydub_data):
        return jsonify({ "error": pydub_data["error"] })
    song = pydub_data["song"]
    start = song[:json_data["startTime"]]
    end = song[json_data["endTime"]:]
    spliced = start + end
    base64_audio = pydub_to_b64_ascii(spliced, pydub_data["format"])
    return jsonify(base64_audio)

@app.route('/supportedFormats', methods=['GET'])
def get_supported_formats():
    return jsonify(["mp3","flac","wav","ogg","m4a"]);

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

@app.route('/downloadAlbumArt', methods=['POST'])
def getArt():
    json_data = request.json
    artist = json_data["artist"]
    album = json_data["album"]
    downloadArtCover(artist,album)
    return "Downloaded"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    return render_template('index.html')

# ------------------------------------- END ROUTES -------------------------------------


# ------------------------------------- FUNCTIONS --------------------------------------
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

def b64_ascii_to_pillow(b64Image=-1):
    # Converts client supplied b64 ascii image data with to pillow Image
    try:
        if(b64Image == -1):
            return {"error":"Missing image data from upload"}

        # Decode b64 ascii data to get bytes (a file-like object)
        byte_data = base64.b64decode(b64Image)

        img = Image.open(io.BytesIO(byte_data))

        return {"image":img}
    except:
        return -1

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

def downloadArtCover(artist, album):
    file_size = int('300') #Width and Height
    file_path = "./cover.jpg"
    subprocess.call([r"./sacad.exe", str(artist), str(album), str(file_size), str(file_path)])

def format_to_contentType(f):
    return {
        'mp3': "audio/mp3",
        'mpeg': "audio/mp3",
        'flac': "audio/flac",
        'wav' : "audio/wav",
        'ogg' : "audio/ogg",
        'm4a' : "audio/m4a"
    }.get(f, "audio/mp3")   # If type not found, default on mp3

def image_url_to_pillow(url):
    try:
        url_response = urllib.request.urlopen(url).read()
        img = Image.open(io.BytesIO(url_response))
        return img
    except:
        return -1

def pillow_image_to_b64_ascii(byte_data):
    # Force converts to jpeg for simplicity
    buffered = io.BytesIO()
    rgb_im = byte_data.convert('RGB')
    rgb_im.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('ascii')
    return {
        "contentType" : "image/jpeg",
        "base64" : img_str
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



# ----------------------------------- END FUNCTIONS ------------------------------------
