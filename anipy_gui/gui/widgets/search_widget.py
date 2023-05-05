import threading
from gi.repository import GLib
from loguru import logger
from anipy_cli import query, config, Entry
from typing import List

from anipy_gui.gui.widgets.anime_view import AnimeView, AnimeWidget
from anipy_gui.anime import Anime
from anipy_gui.gui.widgets.anime_revealer import RevealerAction


class AnimeSearchWidget(AnimeView):
    def __init__(self, application, revealer_actions: List[RevealerAction]):
        super().__init__(application=application, revealer_actions=revealer_actions)
        self.search_thread = None
        self.searching = False

    def search_thread_target(self, anime_query: str):
        GLib.idle_add(self.clear_grid)
        GLib.idle_add(self.start_loading)
        logger.debug("Starting search for {}", anime_query)
        query_cls = query(anime_query, Entry())
        links_n_names = query_cls.get_links()

        logger.debug("Found {}", links_n_names)
        if links_n_names == 0:
            self.searching = False
            GLib.idle_add(self.stop_loading)
            return

        widgets = []
        for l, n in zip(*links_n_names):
            gogo_url = config.Config().gogoanime_url
            anime = Anime(show_name=n, category_url=gogo_url + l)
            anime_widget = AnimeWidget(anime=anime, img_loader=anime.get_image)
            widgets.append(anime_widget)

        for i in widgets:
            self.add_anime_widget(i)

        GLib.idle_add(self.stop_loading)
        GLib.idle_add(self.show_all)
        self.searching = False

    def start_search(self, query: str):
        self.search_thread = threading.Thread(
            target=self.search_thread_target, args=(query,)
        )
        self.search_thread.daemon = True
        self.searching = True
        self.search_thread.start()
