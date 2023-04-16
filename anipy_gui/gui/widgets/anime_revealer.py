from typing import Callable, List
from gi.repository import Gtk, Gdk, Pango
from loguru import logger

from anipy_gui.anime import Anime


class AnimeRevealer(Gtk.Revealer):
    def __init__(
        self,
        play_callback: Callable[[Anime], None],
        download_callback: Callable[[Anime], None],
    ):
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

        self.play_button = Gtk.Button.new_with_label("Play")
        self.play_button.set_image(
            Gtk.Image.new_from_icon_name(
                "media-playback-start", Gtk.IconSize.LARGE_TOOLBAR
            )
        )
        self.play_button.set_always_show_image(True)
        self.play_button.set_relief(Gtk.ReliefStyle.NONE)
        self.play_button.set_focus_on_click(False)
        self.play_button.connect("clicked", lambda _: play_callback(self.anime))

        self.download_button = Gtk.Button.new_with_label("Download")
        self.download_button.set_image(
            Gtk.Image.new_from_icon_name("download", Gtk.IconSize.LARGE_TOOLBAR)
        )
        self.download_button.set_always_show_image(True)
        self.download_button.set_relief(Gtk.ReliefStyle.NONE)
        self.download_button.set_focus_on_click(False)
        self.download_button.connect("clicked", lambda _: download_callback(self.anime))

        self.box.pack_start(self.anime_label, True, True, 0)
        self.box.pack_start(self.play_button, False, False, 0)
        self.box.pack_start(self.download_button, False, False, 0)

        self.add(self.box)

    def set_anime(self, anime: Anime):
        self.anime = anime
        self.anime_label.set_text(anime.show_name)
        self.show_all()
