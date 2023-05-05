from gi.repository import Gtk, Gdk, GLib
from loguru import logger
from threading import Thread
import time

from anipy_gui.gui.widgets.anime_view import AnimeWidget
from anipy_gui.gui.widgets.player import MpvPlayer
from anipy_gui.gui.widgets.anime_info import AnimeInfoView
from anipy_gui.gui.widgets.spinner_btn import SpinnerButton
from anipy_gui.anime import Anime


class AnimeTabView(Gtk.Notebook):
    def __init__(self, anime: Anime):
        super().__init__()
        self.anime = anime

        self.set_scrollable(True)
        self.set_show_border(False)
        self.set_show_tabs(True)
        self.set_tab_pos(Gtk.PositionType.TOP)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.get_style_context().add_class("animetab-view")

        self.info_view = AnimeInfoView(
            self.anime, self.on_play_anime, self.on_download_anime
        )
        self.append_page(self.info_view, Gtk.Label(self.anime.show_name))

        self.player = None
        self.ep_loader_thread = None

        self.show_all()

    def _on_play_anime(self, wg: SpinnerButton, episode):
        GLib.idle_add(wg.start_spinner)
        video_link = self.anime.get_video_link(episode)

        if self.player is None:
            self.player = MpvPlayer()
            self.append_page(self.player, Gtk.Label("Player"))
            self.show_all()

        self.player.play(video_link)
        self.set_current_page(1)
        self.player.grab_focus()
        GLib.idle_add(wg.stop_spinner)

    def close_player(self):
        if self.player is not None:
            #self.player.destroy()
            self.player.area.mpv.terminate()
            self.player.remove(self.player.area)
            self.player = None
            self.remove_page(1)

    
    def on_play_anime(self, wg: SpinnerButton, episode):
        if self.ep_loader_thread is not None:
            if self.ep_loader_thread.is_alive():
                return
        self.ep_loader_thread = Thread(target=self._on_play_anime, args=(wg, episode,))
        self.ep_loader_thread.start()


    def on_download_anime(self, wg, episode):
        logger.info(f"Downloading is not implemented yet")
