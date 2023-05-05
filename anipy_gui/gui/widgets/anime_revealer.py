from typing import Callable, List
from gi.repository import Gtk, Gdk, Pango
from loguru import logger
from dataclasses import dataclass

from anipy_gui.anime import Anime


@dataclass
class RevealerAction:
    name: str
    callback: Callable[[Anime], None]
    icon_name: str


class AnimeRevealer(Gtk.Revealer):
    def __init__(self, reveal_actions: List[RevealerAction]):
        super().__init__()
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self.set_transition_duration(500)

        self.anime = None

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.box.get_style_context().add_class("revealer-box")

        self.anime_label = Gtk.Label()
        self.anime_label.set_margin_start(10)
        self.anime_label.set_margin_end(5)
        self.anime_label.set_margin_top(5)
        self.anime_label.set_margin_bottom(5)
        self.anime_label.set_justify(2)
        self.anime_label.set_halign(1)
        self.anime_label.set_valign(1)
        self.anime_label.set_line_wrap(True)
        self.anime_label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.box.pack_start(self.anime_label, True, True, 0)

        for action in reveal_actions:
            button = Gtk.Button.new_with_label(action.name)
            button.set_image(
                Gtk.Image.new_from_icon_name(
                    action.icon_name, Gtk.IconSize.LARGE_TOOLBAR
                )
            )
            button.set_always_show_image(True)
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.set_focus_on_click(False)
            button.connect("clicked", lambda _: action.callback(self.anime))
            self.box.pack_end(button, False, False, 0)

        self.add(self.box)

    def set_anime(self, anime: Anime):
        self.anime = anime
        self.anime_label.set_text(anime.show_name)
        self.show_all()
