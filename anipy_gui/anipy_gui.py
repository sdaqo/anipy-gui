#!/bin/python
# TODO:
    # - add listwidget to search Results - done
    # - add quality selection
    # - add player shortcuts for next/prev
    # - register app/desktop file
    # - add settings
    # - add search history - done only proper path misses

import sys
import mpv
import time
import requests
import anipy_cli
import os
from pathlib import Path
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *

FONT_SIZE = 16
BASE_URL = anipy_cli.config.gogoanime_url
SEARCH_HISTORY_PATH =  Path(Path(__file__).parent) / "search_history.txt"
ASSETS_PATH = Path(Path(__file__).parent) / "assets"

class ErrorPopup(QMessageBox):
    def __init__(self, errstr):
        super().__init__()
        self.setText(errstr)
        self.exec()

class MainWin(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("anipy-gui")
        self.setWindowIcon(QIcon(str(ASSETS_PATH / "icon.ico")))
        self.central_widget = TabWidget(self).return_widget()
        self.setCentralWidget(self.central_widget)
        self.menu()
        self.show()
    
    def menu(self):
        mainMenu = self.menuBar()
        hist_menu = mainMenu.addMenu('History')
        
        show_hist_action = QAction('Show History', self)
        show_hist_action.triggered.connect(self.show_history)
        show_hist_action.setShortcut('Ctrl+H')

        hist_menu.addAction(show_hist_action)
        hist_menu.addAction('Clear History', self.clear_history)
        hist_menu.addAction('Clear Search History', self.clear_search_hist)

    def show_history(self):
        self.history_widget = HistoryWidget(self, self.central_widget).get_widget()
        self.central_widget.addTab(self.history_widget, "History")
        self.central_widget.setCurrentWidget(self.history_widget)
    def clear_search_hist(self):
        try:
            os.remove('s_hist.txt')
        except FileNotFoundError:
            pass

    def clear_history(self):
        try:
            anipy_cli.config.history_file_path.unlink()
        except FileNotFoundError:
            pass

class TabWidget(QTabWidget):

    def __init__(self, mainwin):
        super().__init__()
        self.mainwin = mainwin
        #self.setStyleSheet("background-color: white; color: black;")
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.add_search()
    
    def close_tab(self, index):
        if index == 0:
            return
        try:
            widget = self.widget(index)
            widget.mpv_widget.exit()
            widget.mpv_widget.player.termintate()
        except:
            pass

        self.removeTab(index)


    def return_widget(self):
        return self

    def add_search(self):
        self.search_widget = SearchWidget(self.mainwin, self).create_search_widget()
        self.addTab(self.search_widget, "Search")
        self.setCurrentWidget(self.search_widget)

def _write_to_search_history(search_str):
    list = _read_from_search_history()
    list = [x.replace('\n', '') for x in list]
    with open(SEARCH_HISTORY_PATH, 'w') as f:
        if search_str in list:
            index = list.index(search_str)
            list.pop(index)
        list.append(search_str)
        for i in list:
            f.write(i+'\n')

def _read_from_search_history():
    try:
        with open(SEARCH_HISTORY_PATH, 'r') as f:
            list = f.readlines()
            return list
            
    except FileNotFoundError:
        return []

class SearchWidget(QWidget):
    def __init__(self, main_win, tab_widget):
        super().__init__()
        self.main_win = main_win
        self.tab = tab_widget

    
    def create_search_widget(self):
        self.formLay = QFormLayout()
        self.search_box()
        self.setLayout(self.formLay)
        return self
    
    def search_box(self):
        self.sbox = QComboBox()
        hist = _read_from_search_history()
        hist.reverse()
        self.sbox.addItems(hist)
        self.sbox.setEditable(True)
        self.sbox.setFont(QFont("Arial", FONT_SIZE))
        self.sbox.setPlaceholderText("Search Animes")
        self.sbox.editTextChanged.connect(self.retrieve_text)
        self.sbox.installEventFilter(self)
        self.sbox.clearEditText()
        self.formLay.addRow(None, self.sbox)
    
    def eventFilter(self, source, event):
        if (event.type() == QEvent.KeyPress and
            event.key() == Qt.Key_Return):
            self.start_query()
            return True
        return super().eventFilter(source, event)

    def retrieve_text(self, text):
        self.text = text

    def start_query(self):
        self.text = self.text.strip()
        _write_to_search_history(self.text)
        item = self.sbox.findText(self.text)
        if item != -1:
            self.sbox.removeItem(item)
        self.sbox.insertItem(0, self.text)
        entry = anipy_cli.entry()
        site_query = anipy_cli.query(self.text, entry)
        links = site_query.get_links()

        if links == 0:
            ErrorPopup("No Search Results")
            return

        try:
            # dont create multiple lists
            self.formLay.removeWidget(self.listwidget)
            self.listwidget.deleteLater()
            self.listwidget = None
            self.list_box(links)
        except:
            self.list_box(links)

    def list_box(self, query_result):
        self.links = query_result[0]
        self.names = query_result[1]
        self.listwidget = QListWidget()
        self.listwidget.setFont(QFont("Arial", FONT_SIZE))
        for i, x in zip(self.links, self.names):
            item = QListWidgetItem()
            widget = ListWidget(x,
                                i,
                                self.tab,
                                self.main_win,
                                ).create_widget()

            item.setSizeHint(widget.sizeHint())
            self.listwidget.addItem(item)
            self.listwidget.setItemWidget(item, widget)

        self.formLay.addRow(None, self.listwidget)

class AnimePage(QStackedWidget):
    def __init__(self, name, link, main_win, tab, default_ep=None):
        super().__init__()
        self.name = name
        self.tab = tab
        self.mainwin = main_win
        self.link = BASE_URL + link
        self.lay = QFormLayout()
        self.default_ep = default_ep
        widget = self.create_widget()
        self.addWidget(widget)
        self.setCurrentWidget(widget)
    
    def create_tab(self):
        return self

    def anime_info_widget(self):
        info = anipy_cli.get_anime_info(self.link)
        
        r = requests.get(info['image_url'])
        pix = QPixmap()
        pix.loadFromData(r.content)
        pix = pix.scaled(300, 395, aspectRatioMode=Qt.KeepAspectRatio)


        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignLeft)
        
        box = QGroupBox()
        box.setLayout(hbox)
        box.setFont(QFont("Arial", FONT_SIZE))
        box.setTitle(self.name)
        
        lable = QLabel()
        lable.setPixmap(pix)
        hbox.addWidget(lable)
        
        text_string = f"{info['synopsis']}\n\n{info['type']}\nGenres: {', '.join(info['genres'])}\nReleas Year: {info['release_year']}\nStatus: {info['status']}"
        lable_2 = QLabel()
        lable_2.setFont(QFont("Arial", 12))
        lable_2.setText(text_string)
        lable_2.setWordWrap(True)
        lable_2.setAlignment(Qt.AlignTop)
        hbox.addWidget(lable_2)   


        self.lay.addRow(box)


    def episode_list(self):
        self.entry = anipy_cli.entry()
        self.entry.category_url = self.link
        ep_class = anipy_cli.epHandler(self.entry)
        ep_list = list(range(1, ep_class.get_latest() + 1))
        ep_list = map(str, ep_list)
        listwg = QListWidget()
        listwg.setFont(QFont("Arial", FONT_SIZE))
        listwg.addItems(ep_list)
        listwg.currentItemChanged.connect(lambda a: self.play_ep(a))
        if self.default_ep != None:
            listwg.setCurrentRow(self.default_ep)

        self.lay.addRow(None, listwg)
    
    def play_ep(self, ep):
        self.entry.name = self.name
        self.entry.ep = int(ep.text())
        self.entry = anipy_cli.epHandler(self.entry).gen_eplink()
        try:
            # dont create multiple ep_opts
            self.lay.removeWidget(self.box_ep_opts)
            self.box_ep_opts.deleteLater()
            self.box_ep_opts = None
            self.ep_opts()
        except:
            self.ep_opts()

    def ep_opts(self):
        hbox_lay = QHBoxLayout()

        self.box_ep_opts = QGroupBox()
        self.box_ep_opts.setLayout(hbox_lay)
        self.box_ep_opts.setAlignment(Qt.AlignTop)
        self.box_ep_opts.setFont(QFont("Arial", FONT_SIZE))
        self.box_ep_opts.setTitle(self.name + f" - EP: {self.entry.ep}")

        play_button = QPushButton()
        play_button.setText("Play Episode")
        play_button.setFont(QFont("Arial", FONT_SIZE))
        play_button.clicked.connect(lambda a: self.watch_receiver(a))
        hbox_lay.addWidget(play_button)

        dl_button = QPushButton()
        dl_button.setText("Download Episode")
        dl_button.setFont(QFont("Arial", FONT_SIZE))
        dl_button.clicked.connect(lambda a: self.dl_signal_receiver(a))
        hbox_lay.addWidget(dl_button)

        self.lay.addRow(self.box_ep_opts)

    def dl_signal_receiver(self, signal):

        self.lay.removeWidget(self.box_ep_opts)
        self.box_ep_opts.deleteLater()
        self.box_ep_opts = None

        self.field = QTextEdit()
        self.lay.addRow(self.field)

        self.entry.embed_url = ""
        url_class = anipy_cli.videourl(self.entry, None)
        url_class.stream_url()
        self.entry = url_class.get_entry()
        dl_class = anipy_cli.download(self.entry)
        t1 = Thread(target=dl_class.download)
        t1.start()


    def redirect_stdout(self):

        f = io.StringIO()
        redirect_stdout(f)
        s = f.getvalue()
        print(s)
        self.field.setText(s)


    def watch_receiver(self, data):
        self.entry.show_name = self.name
        self.mpv_widget = MpvPage(self.entry, self, self.mainwin, self.tab)
        self.addWidget(self.mpv_widget)
        self.setCurrentIndex(1)

    def dl_anime(self):
       pass 

    def create_widget(self):
        widget = QWidget()
        self.anime_info_widget()
        self.episode_list()
        widget.setLayout(self.lay)
        return widget

class MpvPage(QWidget):
    def __init__(self, entry, stack, mainwin, tab):
        super().__init__()
        
        self.main_win = mainwin
        self.tab = tab
        self.stack = stack
        self.entry = entry
        self.max = False
        self.fs = False
        self.cursor = True
        self.embed_mpv()
        self.setMouseTracking(True)

    def stream_url(self):
        self.entry.embed_url = ""
        url_class = anipy_cli.videourl(self.entry, None)
        url_class.stream_url()
        self.entry = url_class.get_entry()

    def embed_mpv(self):
        import locale
        locale.setlocale(locale.LC_NUMERIC, 'C')
        self.stream_url()
        self.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.setAttribute(Qt.WA_NativeWindow)
        self.player = mpv.MPV(
                         wid=str(int(self.winId())),
                         osc=True,
                         player_operation_mode='pseudo-gui',
                         script_opts='osc-layout=box,osc-seekbarstyle=bar,osc-deadzonesize=0',
                         input_default_bindings=True,
                         input_vo_keyboard=True,
                         force_media_title=f"{self.entry.show_name} - EP: {self.entry.ep} - {self.entry.quality}",
                         http_header_fields=f"Referer: {self.entry.embed_url}")
        
        self.player.play(self.entry.stream_url)
        anipy_cli.history(self.entry).write_hist()

        @self.player.property_observer('fullscreen')
        def fullscreen(_name, value):
            if value == True:
                self.fullscreen()

            else:
                self.exit_fullscreen()


        @self.player.on_key_press('q')
        def exit_player():
            self.exit()
            del self.player

        @self.player.on_key_press('h')
        def toggle_cursor():
            if self.cursor == True:
                self.stack.setCursor(Qt.BlankCursor)
                self.cursor = False

            elif self.cursor == False:
                self.stack.unsetCursor()
                self.cursor = True

        @self.player.on_key_press('b')
        def prev_episode():
            ep_class = anipy_cli.epHandler(self.entry)
            self.entry = ep_class.prev_ep()
            self.stream_url()
            self.player.force_media_title = f"{self.entry.show_name} - EP: {self.entry.ep} - {self.entry.quality}"
            self.player.play(self.entry.stream_url)
            anipy_cli.history(self.entry).write_hist()
        
        @self.player.on_key_press('n')
        def next_episode():
            ep_class = anipy_cli.epHandler(self.entry)
            self.entry = ep_class.next_ep()
            self.stream_url()
            self.player.force_media_title = f"{self.entry.show_name} - EP: {self.entry.ep} - {self.entry.quality}"
            self.player.play(self.entry.stream_url)
            anipy_cli.history(self.entry).write_hist()
    
    def fullscreen(self):
        self.max = self.main_win.isMaximized()
        self.main_win.showFullScreen()
        self.main_win.menuBar().setVisible(False)
        self.tab.tabBar().hide()
        self.tab.setStyleSheet("border: 0px;")
        self.fs = True
        self.main_win.show()

    def exit_fullscreen(self):
        self.main_win.menuBar().setVisible(True)
        self.tab.tabBar().show()
        self.tab.setStyleSheet("")
        if self.max:
            self.main_win.showNormal()
            self.main_win.showMaximized()
        else:
            self.main_win.showNormal()

        self.fs = False
        self.main_win.show()
    
    def exit(self):
        self.player.quit()
        self.exit_fullscreen()
        self.stack.unsetCursor()
        curr_widget = self.stack.currentWidget()
        self.stack.removeWidget(curr_widget)
        self.stack.setCurrentIndex(1)

class HistoryWidget(QWidget):
    def __init__(self, mainwin, tab):
        super().__init__()
        self.lay = QFormLayout()
        self.main_win = mainwin
        self.tab = tab

    def format_history(self):
        items = []
    
    def history_list(self):
        hist = anipy_cli.history(anipy_cli.entry).read_save_data()
        
        list_widget = QListWidget()
        for i in hist:
            item = QListWidgetItem()
            widget = ListWidget(i,
                                hist[i]['category-link'],
                                self.tab,
                                self.main_win,
                                ep=hist[i]['ep'],
                                ).create_widget()

            item.setSizeHint(widget.sizeHint())
            list_widget.addItem(item)
            list_widget.setItemWidget(item, widget)

        self.lay.addRow(list_widget)

    def get_widget(self):
        self.history_list()
        self.setLayout(self.lay)
        return self

class ListWidget(QWidget):
    def __init__(self, name, url, tab, main_win, ep: int = None):
        super().__init__()
        self.lay = QHBoxLayout()
        self.name = name
        self.main_win = main_win
        self.tab = tab
        self.ep = ep
        self.url = url.replace(BASE_URL, "")
        self.label_name = name
        if ep != None:
            self.ep = self.ep - 1
            self.label_name = f"{name} - Episode: {ep}"

    def create_widget(self):
        label = QLabel(self.label_name)
        label.setFont(QFont("Arial", FONT_SIZE))
        self.lay.addWidget(label)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.lay.addItem(spacer)
        button = QToolButton()
        button.setIcon(QIcon(str(ASSETS_PATH / "play_icon.png")))
        button.setIconSize(QSize(35, 25))
        button.setFont(QFont("Arial", FONT_SIZE))
        button.clicked.connect(lambda a: self.switch_to_tab())
        self.lay.addWidget(button)
        self.setLayout(self.lay)
        return self
    
    def switch_to_tab(self):
        anime_page = AnimePage(self.name,
                               self.url,
                               self.main_win,
                               self.tab,
                               self.ep).create_tab()
        self.tab.addTab(anime_page, self.name)
        self.tab.setCurrentWidget(anime_page)

def main():
    app = QApplication(sys.argv)
    ex = MainWin()
    w = 1300; h = 1000
    ex.resize(w, h)
    sys.exit(app.exec_())
