#import everything from everywhere
__requires__ = 'sacad==2.1.1'
# from pydub import AudioSegment
# from pydub.playback import play
# import mutagen
# import urllib.request
# from mutagen.mp3 import MP3
# from mutagen.flac import FLAC
# from mutagen.id3 import ID3, APIC, error
import subprocess

#link = "https://en.wikipedia.org/wiki/2014_Forest_Hills_Drive#/media/File:2014ForestHillsDrive.jpg"
#urllib.request.urlretrieve(link,"alfsdkjlgfohqw.jpg")
# audio = MP3("logic2.mp3", ID3=ID3)


artisttest = "J Cole"
albumtest = "Cole World"
sizetest = int('600')
pathtest =  "cover.jpg"
# print(sizetest)
# print(type(int(sizetest)))
#subprocess.call(r"C:/Users/Adrian/Desktop/205project/sacad.exe", artist=artist, album=album, size=int(size), out_filepath=path)
subprocess.check_call([r"C:/Users/Adrian/Desktop/205project/sacad.exe", str(artisttest), str(albumtest), str(sizetest), str(pathtest)])

# add ID3 tag if it doesn't exist
# try:
#     audio.add_tags()
# except error:
#     pass
#
# audio.tags.add(
#     APIC(
#         encoding=3, # 3 is for utf-8
#         mime='image/jpg', # image/jpeg or image/png
#         type=3, # 3 is for the cover image
#         desc=u'Cover',
#         data=open('cover.jpg', 'rb').read()
#     )
# )
#
# audio.save(v2_version=3)
print("done")

#mutagen.File("logic.mp4")

#song = AudioSegment.from_wav("0993.wav")
#//song2 = AudioSegment.from_file("0993.wav", format="wav")
# try:
# 	id3info = ID3('/some/file/moxy.mp3')
	# print id3info
	# id3info['TITLE'] = "Green Eggs and Ham"
	# id3info['ARTIST'] = "Moxy Früvous"
    # for k, v in id3info.items():
    #     print k, ":", v
# except InvalidTagError, message:
#     print "Invalid ID3 tag:", message

#logic = AudioSegment.from_file("logic.mp4", format="mp4")
#logic.export("logic3.mp3", format="mp3")


#song2.export("audio1.mp3", format="mp3")
#play(song)
