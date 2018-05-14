from flask import Flask, render_template, url_for, redirect, request, Response, jsonify, send_file, make_response
from flask_bootstrap import Bootstrap
from PIL import Image
from werkzeug.utils import secure_filename
from pydub import AudioSegment
from PIL import Image
import os, io, base64, pydub, urllib, urllib.request, tempfile

# SACAD IMPORTS
__requires__ = 'sacad==2.1.1'
import subprocess

app= Flask(__name__, static_url_path = "/static", static_folder = "static")
bootstrap = Bootstrap(app)

# --------------------------------------- ROUTES ---------------------------------------

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

# Crops supplied audio based on supplied timestamps
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

# Converts supplied audio to supplied format] and responsds
#   with base64 ascii data to be downloaded client-side
@app.route('/downloadAudio', methods=['POST'])
def downloadAudio():
    json_data = request.json
    format = json_data["download_format"]
    contentType = format_to_contentType(format)

    if(contentType == -1):
        return jsonify({"error":"Format not supported!"})

    song_data = b64_ascii_to_pydub(json_data["base64"], json_data["contentType"])
    if("error" in song_data):
        return jsonify({"error":song_data["error"]})

    # Create instance of pydub audio and convert the song
    song = song_data["song"]
    b64_audio_info = pydub_to_b64_ascii(song,format)

    return jsonify({"song":b64_audio_info["song"],"contentType":contentType})

    # return jsonify({"msg":"Added Album Art!"})

# Converts supplied audio to mp3, embeds the supplied
#   image data as album art, and responsds with base64 ascii
#   data to be downloaded client-side
@app.route('/downloadAudioWithAlbumArt', methods=['POST'])
def downloadAudioWithAlbumArt():
    json_data = request.json

    # Get image and resize for album art
    image_data = b64_ascii_to_pillow(json_data["base64_image"])
    if("error" in image_data):
        return jsonify({"error":image_data["error"]})

    song_data = b64_ascii_to_pydub(json_data["base64_audio"], json_data["contentType_audio"])
    if("error" in song_data):
        return jsonify({"error":song_data["error"]})

    try:
        b64_audio_info = add_album_art_to_pydub(song_data["song"],image_data["image"])
        return jsonify({"song":b64_audio_info["song"],"contentType":json_data["contentType_audio"]})
    except:
        return jsonify({"error":"Incorrect audio or image format"})

    # return jsonify({"msg":"Added Album Art!"})

# Gets the image data from a supplied URL
#   and returns it in base64 ascii
@app.route('/getImageData', methods=['POST'])
def get_image_data():
    # Given an image URL, downloads the b64 image data
    json_data = request.json
    img = image_url_to_pillow(json_data["url"])
    if(img == -1):
        return jsonify({"error":"Invalid Url"})

    # img here is editable in pillow
    # resized = img.resize((300,300))
    img_b64 = pillow_image_to_b64_ascii(img)
    return jsonify(img_b64)

# Splices supplied audio based on supplied timestamps
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

# Returns list of supported audio formats
@app.route('/supportedFormats', methods=['GET'])
def get_supported_formats():
    return jsonify(["mp3","flac","wav","ogg"]);

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

# Base index page render
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    return render_template('index.html')

# ------------------------------------- END ROUTES -------------------------------------


# ------------------------------------- FUNCTIONS --------------------------------------

# Adds pillow image as album art to pydub song
#   creates a jpg tempfile with an addressable name
#   to meet pydub requirement (cant pass in file-like object)
def add_album_art_to_pydub(pydub_song, pillow_image):
    # create a named temporary file with suffix ".jpg" and manual deletion enables
    tf = tempfile.NamedTemporaryFile(suffix=".jpg",delete=False)
    # change permissions of file to be read/write/executable
    os.chmod(tf.name, 0o777)
    # resize and convert pillow image to correct format
    image = pillow_image.convert('RGB').resize((600,600))
    # Open the temp file to write image data
    with open(tf.name,'wb+') as jpg:
        # Read bytes from byte-like object and write them to temp file
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        jpg.write(buffered.getvalue())

    # Save new song as mp3 with the cover linking to our tempfile (image)
    b64_audio_info = pydub_to_b64_ascii(pydub_song,"mp3",tf.name)
    # Close tempfile and delete it from system
    tf.file.close()
    os.unlink(tf.name)
    # Return song data
    return b64_audio_info

# Converts client supplied b64 ascii audio data with
#   specified contentType to pydub formatted song
def b64_ascii_to_pydub(b64Song=-1, contentType=-1):
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

# Converts client supplied b64 ascii image data with to pillow Image
def b64_ascii_to_pillow(b64Image=-1):
    try:
        if(b64Image == -1):
            return {"error":"Missing image data from upload"}

        # Decode b64 ascii data to get bytes (a file-like object)
        byte_data = base64.b64decode(b64Image)

        img = Image.open(io.BytesIO(byte_data))

        return {"image":img}
    except:
        return {"error":"Image formatted incorrectly"}

# Translates contentType supplied from
#  client to audio format used in pydub
def contentType_to_format(cT):
    return {
        'audio/mp3': "mp3",
        'audio/mpeg': "mp3",
        'audio/flac': "flac",
        'audio/wav' : "wav",
        'audio/ogg' : "ogg"
    }.get(cT, -1)   # If type not found, returns -1

def downloadArtCover(artist, album):
    file_size = int('300') #Width and Height
    file_path = "./cover.jpg"
    subprocess.call([r"./sacad.exe", str(artist), str(album), str(file_size), str(file_path)])

# Translates format used in pydub
#   to contentType to be used by client
def format_to_contentType(f):
    return {
        'mp3': "audio/mp3",
        'mpeg': "audio/mp3",
        'flac': "audio/flac",
        'wav' : "audio/wav",
        'ogg' : "audio/ogg"
    }.get(f, -1)   # If type not found, default on mp3

# Extracts image data from url and formats as
#   pillow image
def image_url_to_pillow(url):
    try:
        url_response = urllib.request.urlopen(url).read()
        img = Image.open(io.BytesIO(url_response))
        return img
    except:
        return -1

# Converts pillow formated image into base64 ascii jpg image
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

# Converts pydub formatted audio to b64 ascii format
#   for playing on client side audio player
# AUDIO CONVERSION CAN HAPPEN HERE (exportFormat)
def pydub_to_b64_ascii(pydubSong, exportFormat, image=-1):
    # Export modified audio file to a bytes object (through a bytestream)
    f = io.BytesIO()
    if(image == -1):
        f = pydubSong.export(f, format=exportFormat)
    else:
        f = pydubSong.export(f, format=exportFormat, cover=image)
    f.seek(0)
    song = f.read() # Bytes of modified song

    # b64 ascii encode the bytes to be sent back to the client
    # This part can also be modified to just send the file as a download to the client
    return {
        "song": base64.b64encode(song).decode('ascii'),
        "contentType": format_to_contentType(exportFormat)
    }

# ----------------------------------- END FUNCTIONS ------------------------------------
