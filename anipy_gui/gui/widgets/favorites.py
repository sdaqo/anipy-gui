from gi.repository import Gtk, Gdk
from typing import List

from anipy_gui.gui.widgets.anime_view import AnimeView, AnimeWidget
from anipy_gui.favorites import get_favorites
from anipy_gui.anime import Anime
from anipy_gui.gui.widgets.anime_revealer import RevealerAction


class FavoritesView(AnimeView):
    def __init__(self, application, revealer_actions: List[RevealerAction]):
        super().__init__(application=application, revealer_actions=revealer_actions)

    def load_favorite_animes(self):
        self.clear_grid()
        for i in get_favorites().favorites:
            anime = Anime(show_name=i.show_name, category_url=i.category_url)
            self.add_anime_widget(AnimeWidget(anime=anime, img_loader=anime.get_image))
        self.show_all()
