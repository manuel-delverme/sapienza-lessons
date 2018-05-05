#! /usr/bin/python
import collections
import json
import string
import pprint
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
import sys
import os.path
import vlc
import ipdb
from PyQt5 import QtCore, QtGui, QtWidgets

class Player(QtWidgets.QMainWindow):
    def __init__(self, master=None):
        QtWidgets.QMainWindow.__init__(self, master)

        self.label = None
        self.begin_time = None
        self.end_time = None

        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        self.createUI()
        self.isPaused = False

    def createUI(self):
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        self.hvideobox = QtWidgets.QHBoxLayout()

        if sys.platform == "darwin":
            self.videoframe = QtGui.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtWidgets.QFrame(self)

        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0,0,0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.labels = collections.defaultdict(list)
        with open("wtf.txt", "r") as fin:
            for row in fin:
                group, label = row.strip().split(",")
                # print(group, label)
                self.labels[group].append(label.strip())

        self.labels1_list = QtWidgets.QListWidget()
        self.labels2_list = QtWidgets.QListWidget()

        for k in sorted(self.labels.keys()):
            self.labels1_list.addItem(k)

        self.labels1_list.itemSelectionChanged.connect(self.update_label1)
        self.labels2_list.itemSelectionChanged.connect(self.update_label2)
        self.label_info = QtWidgets.QLabel()

        self.labels1_list.setMaximumWidth(50)
        self.labels2_list.setMaximumWidth(200)
        self.label_info.setMaximumWidth(200)
        self.hvideobox.addWidget(self.labels1_list)
        self.hvideobox.addWidget(self.labels2_list)
        self.hvideobox.addWidget(self.videoframe)
        self.hvideobox.addWidget(self.label_info)

        self.positionslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.valueChanged.connect(self.setPosition)

        self.hbuttonbox = QtWidgets.QHBoxLayout()
        self.playbutton = QtWidgets.QPushButton("Play [Space]")
        self.hbuttonbox.addWidget(self.playbutton)
        self.playbutton.clicked.connect(self.PlayPause)

        self.playshortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Space"), self)
        self.playshortcut.activated.connect(self.PlayPause)

        self.label_begin = QtWidgets.QPushButton("Label Begin [1]")
        self.hbuttonbox.addWidget(self.label_begin)
        self.label_begin.clicked.connect(self.update_begin_label)

        self.label_begin_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("1"), self)
        self.label_begin_shortcut.activated.connect(self.update_begin_label)

        self.label_end = QtWidgets.QPushButton("Label End [2]")
        self.hbuttonbox.addWidget(self.label_end)
        self.label_end.clicked.connect(self.update_end_label)

        self.label_end_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("2"), self)
        self.label_end_shortcut.activated.connect(self.update_end_label)

        self.hack_shortcuts = {}
        # with open("wtf.txt", "r") as fin:
        #     for row_idx, row in enumerate(fin):
        #         sequence = row[row.find("(")+1:row.find(")")]
        #         sequence = "+".join(sequence)
        #         hack_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(sequence), self)

        #         def more_hacks(sequence, row_idx):
        #             def even_more_hacks():
        #                 self.labels1_list.setCurrentRow(row_idx)
        #             return even_more_hacks

        #         hack_shortcut.activated.connect(more_hacks(sequence, row_idx))
        #         self.hack_shortcuts[sequence] = hack_shortcut

        for f_key in [
                    QtCore.Qt.Key_F1,
                    QtCore.Qt.Key_F2,
                    QtCore.Qt.Key_F3,
                    QtCore.Qt.Key_F4,
                ]:
            seq = QtGui.QKeySequence(f_key)
            hack_shortcut = QtWidgets.QShortcut(seq, self)

            def more_hacks(f_key):
                def even_more_hacks():
                    idx = f_key -  QtCore.Qt.Key_F1
                    self.labels1_list.setCurrentRow(idx)
                return even_more_hacks

            hack_shortcut.activated.connect(more_hacks(f_key))
            self.hack_shortcuts[f_key] = hack_shortcut


        for letter in string.ascii_lowercase:
            hack_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(letter), self)

            def more_hacks(my_letter):
                def even_more_hacks():
                    try:
                        selected_row = self.labels2_list.selectedIndexes()[0].row()
                    except IndexError:
                        selected_row = 0

                    for idx in range(selected_row + 1, self.labels2_list.count()):
                        el = self.labels2_list.item(idx)
                        if el.text()[0].lower() == my_letter:
                            self.labels2_list.setCurrentRow(idx)
                            break
                return even_more_hacks

            hack_shortcut.activated.connect(more_hacks(letter))
            self.hack_shortcuts[letter] = hack_shortcut

        for letter in string.ascii_lowercase:
            hack_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Shift+" + letter), self)

            def more_hacks(my_letter):
                def even_more_hacks():
                    try:
                        selected_row = self.labels1_list.selectedIndexes()[0].row()
                    except IndexError:
                        selected_row = 0

                    for idx in range(0, selected_row)[::-1]:
                        el = self.labels1_list.item(idx)
                        if el.text()[0].lower() == my_letter:
                            self.labels1_list.setCurrentRow(idx)
                            break
                return even_more_hacks
            hack_shortcut.activated.connect(more_hacks(letter))
            self.hack_shortcuts["-" + letter] = hack_shortcut


        self.hbuttonbox.addStretch(1)
        self.save_button = QtWidgets.QPushButton("Save [Enter]")
        self.save_button.setEnabled(False)
        self.hbuttonbox.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_label)

        self.save_button_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Return"), self)
        self.save_button_shortcut.activated.connect(self.save_label)

        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.addLayout(self.hvideobox)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.widget.setLayout(self.vboxlayout)

        open_file = QtWidgets.QAction("&Open", self)
        open_file.triggered.connect(self.OpenFile)
        exit = QtWidgets.QAction("&Exit", self)
        exit.triggered.connect(sys.exit)
        lol = QtWidgets.QAction("DoNotClick", self)
        lol.triggered.connect(self.do_lol)

        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(open_file)
        filemenu.addAction(lol)
        filemenu.addSeparator()
        filemenu.addAction(exit)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.updateUI)

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play [Space]")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            self.playbutton.setText("Pause [Space]")
            self.timer.start()
            self.isPaused = False

    def Stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")

    def update_begin_label(self):
        self.begin_time = self.mediaplayer.get_time()
        self._update_label_info()

    def update_end_label(self):
        self.end_time = self.mediaplayer.get_time()
        self._update_label_info()

    def update_label1(self):
        # ipdb.set_trace()
        label, = self.labels1_list.selectedItems()
        label = label.text()
        self.label = label

        self.labels2_list.clear()
        for row in sorted(self.labels[label]):
            self.labels2_list.addItem(row)

        self._update_label_info()

    def update_label2(self):
        # ipdb.set_trace()
        label, = self.labels1_list.selectedItems()
        self.label += ":" + label.text()
        self._update_label_info()


    def save_label(self):
        label_from, label_to = self.begin_time, self.end_time
        label_name = self.label

        if label_from >= label_to:
            self.label_info.setText("WANING!\nLabel End cannot come\nbefore Label Start\nno time travelling\n"+"WARNING!\n"*20)
            self.save_button.setEnabled(False)
            return

        if None in (self.file_name, self.label, self.begin_time, self.end_time):
            print("SHOUDL NOT HAPPEN")
            self.save_button.setEnabled(False)
            return

        json_entry = {
                self.file_name: [
                    {
                        'label': label_name,
                        'frame': [label_from, label_to],
                    },
                ]
        }
        with open("temp.jsonl", "a") as fout:
            json.dump(json_entry, fout)
            fout.write("\n")

        self.save_button.setEnabled(False)
        self.label = None
        self.begin_time = None
        self.end_time = None
        self._update_label_info()

    def _update_label_info(self):
        self.label_info.setText(
        """
        file: {}
        label: {}
        from: {}
        to: {}
        """.format(self.file_name, self.label, self.begin_time, self.end_time))
        if None not in (self.file_name, self.label, self.begin_time, self.end_time):
            self.save_button.setEnabled(True)

    def save_annotation(self):
        print("start", self.begin_label, "end", self.end_time, "label", self.label)

    def do_lol(self):
        import subprocess
        import random
        orientation = random.choice(["normal", "right", "left", "inverted"])
        _ = subprocess.Popen('xrandr -o {}'.format(orientation) ,shell=True, stdout=subprocess.PIPE).communicate()[0]


    def OpenFile(self, filename=None):
        if filename is None or filename == False:
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser('~'))
        self.file_name = filename

        if sys.version < '3':
            filename = unicode(filename)
        self.media = self.instance.media_new(filename)
        self.mediaplayer.set_media(self.media)

        self.media.parse()
        self.setWindowTitle(self.media.get_meta(0))

        if sys.platform.startswith('linux'): # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(self.videoframe.winId())
        self.PlayPause()
        self._update_label_info()

    def setPosition(self, position):
        self.mediaplayer.set_position(position / 1000.0)

    def updateUI(self):
        self.positionslider.blockSignals(True)
        self.positionslider.setValue(self.mediaplayer.get_position() * 1000)
        self.positionslider.blockSignals(False)
        # if not self.mediaplayer.is_playing():
        #     # no need to call this function if nothing is played
        #    self.timer.stop()
        #     if not self.isPaused:
        #       # after the video finished, the play button stills shows
        #       # "Pause", not the desired behavior of a media player
        #       # this will fix it
        #       self.Stop()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    player = Player()
    player.show()
    player.resize(640, 480)
    if sys.argv[1:]:
        player.OpenFile(sys.argv[1])
    sys.exit(app.exec_())
