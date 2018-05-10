import sys
import os
import youtube_dl
from pydub import AudioSegment
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLineEdit,
                                QLabel, QComboBox, QPushButton, QTextBrowser)
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtCore import pyqtSlot, Qt

def timeconv(time):
    minutes, seconds = time.split(':')
    minutes = int(minutes)
    seconds = int(seconds)
    minutes = minutes * 60 * 1000
    seconds = seconds * 1000
    totaltime = minutes + seconds
    return totaltime

def convert(songname, name, type):
    songname.export('{}.{}'.format(name, type), format = type)


class YouTube(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(350, 100, 200, 100)
        self.setWindowTitle('Youtube Downloader')
        self.label = QLabel('Enter Video URL:')
        self.urledit = QLineEdit()
        self.accept = QPushButton('Download', self)
        self.label2 = QLabel('Enter New Filename:')
        self.nameedit = QLineEdit()
        ytlayout = QGridLayout()
        ytlayout.addWidget(self.label, 0, 0)
        ytlayout.addWidget(self.urledit, 0, 1)
        ytlayout.addWidget(self.accept, 2 , 1)
        ytlayout.addWidget(self.label2, 1, 0)
        ytlayout.addWidget(self.nameedit, 1, 1)
        self.accept.clicked.connect(self.clicky)

        self.setLayout(ytlayout)

    @pyqtSlot()
    def clicky(self):
        outtmpl = self.nameedit.text() + '.%(ext)s'
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
        song = AudioSegment.from_file('{}.mp3'.format(self.nameedit.text()), format = 'mp3')
        self.hide()

        
class AudioEdit(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 250, 200)
        self.setWindowTitle('Audio Editing')

        self.lbl = QLabel('File Selector')
        self.cutbtn = QPushButton('Cut', self)
        self.splicebtn = QPushButton('Splice', self)
        self.startbar = QLineEdit()
        self.endbar = QLineEdit()
        self.slbl = QLabel('Start Time')
        self.elbl = QLabel('End Time')
        self.cutbtn.clicked.connect(self.cutfunc)
        self.splicebtn.clicked.connect(self.splicefunc)
        self.fileselector = QLineEdit()
        self.ytbtn = QPushButton('Download Youtube Song')
        self.ytedit = QLineEdit()
        self.convbox = QComboBox()
        self.convbox.addItems(['mp3','wav', 'flac', 'ogg', 'flv'])
        self.convbtn = QPushButton('Convert', self)
        self.convbtn.clicked.connect(self.convfunc)
        self.ytbtn.clicked.connect(self.ytdlfunc)
        layout = QGridLayout()
        layout.addWidget(self.lbl, 0, 0)
        layout.addWidget(self.fileselector, 1, 0)
        layout.addWidget(self.ytbtn, 1, 2)
        layout.addWidget(self.slbl, 2, 0)
        layout.addWidget(self.elbl, 2, 2)
        layout.addWidget(self.startbar, 3, 0)
        layout.addWidget(self.endbar, 3, 2)
        layout.addWidget(self.cutbtn, 4, 0)
        layout.addWidget(self.splicebtn, 4, 2)
        layout.addWidget(self.convbox, 5, 0)
        layout.addWidget(self.convbtn, 5, 2)

        self.setLayout(layout)

    def getsong(self):
        path = self.fileselector.text().split('\\')
        print(path)
        name , type = path[-1].split('.')
        global song
        song = AudioSegment.from_file('{}.{}'.format(name,type),format = type)
    @pyqtSlot()
    def cutfunc(self):
        self.getsong()
        start = timeconv(self.startbar.text())
        end = timeconv(self.endbar.text())
        cutsong = song[start:end]
        convert(cutsong, 'cut', self.convbox.currentText())
        print('Cut Complete')

    @pyqtSlot()
    def splicefunc(self):
        self.getsong()
        start = timeconv(self.startbar.text())
        end = timeconv(self.endbar.text())
        begin = song[:start]
        finish = song[end:]
        spliced = begin + finish
        convert(spliced, 'sliced', self.convbox.currentText())
        print('Splice Complete')

    @pyqtSlot()
    def convfunc(self):
        self.getsong()
        convert(song, 'whatwhat', self.convbox.currentText())

    @pyqtSlot()
    def ytdlfunc(self):
            self.SW = YouTube()
            self.SW.show()



app = QApplication(sys.argv)
w = AudioEdit()
w.show()
sys.exit(app.exec_())
