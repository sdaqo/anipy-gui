from gi.repository import Gtk, Gdk, GLib
from loguru import logger
from threading import Thread
import time


from anipy_gui.gui.widgets.anime_view import AnimeWidget
from anipy_gui.gui.widgets.player import MpvPlayer
from anipy_gui.gui.widgets.anime_info import AnimeInfoView
from anipy_gui.gui.widgets.spinner_btn import SpinnerButton
from anipy_gui.anime import Anime


class AnimeTabView(AnimeInfoView):
    def __init__(self, anime: Anime):
        self.anime = anime
        super().__init__(anime, self.on_play_anime, self.on_download_anime)
        self.get_style_context().add_class("animetab-view")

        self.connect("destroy", self.on_destroy)


        self.player = None
        self.ep_loader_thread = None

        self.show_all()
    
    def on_destroy(self, *args):
        if self.player is not None:
            self.player.destroy()
            self.player = None

    def _on_play_anime(self, wg: SpinnerButton, episode):
        GLib.idle_add(wg.start_spinner)
        video_link = self.anime.get_video_link(episode)
        if video_link is None:
            GLib.idle_add(wg.stop_spinner)
            return

        if self.player is None:
            self.player = MpvPlayer(self.anime, self.on_player_shutdown)

        self.player.play_episde(episode, video_link)
        GLib.idle_add(wg.stop_spinner)
    
    def on_player_shutdown(self):
        self.player = None

    def on_play_anime(self, wg: SpinnerButton, episode):
        if self.ep_loader_thread is not None:
            if self.ep_loader_thread.is_alive():
                return
        self.ep_loader_thread = Thread(target=self._on_play_anime, args=(wg, episode,))
        self.ep_loader_thread.start()


    def on_download_anime(self, wg, episode):
        logger.info(f"Downloading is not implemented yet")
