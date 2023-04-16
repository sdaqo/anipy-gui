from gi.repository import Gtk, Gdk

from anipy_gui.anime import Anime


class FavoriteButton(Gtk.Button):
    def __init__(self, anime: Anime):
        super().__init__()
        self.anime = anime

        self.fav_icon = Gtk.Image.new_from_icon_name(
            "starred-symbolic", Gtk.IconSize.BUTTON
        )
        self.fav_icon.override_color(Gtk.StateFlags.NORMAL, self.get_fav_icon_color())

        self.add(self.fav_icon)
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.set_valign(Gtk.Align.START)
        self.set_halign(Gtk.Align.END)
        self.set_margin_top(5)
        self.set_margin_end(5)
        self.connect("clicked", self.onclick)
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 0.5))

    def get_fav_icon_color(self) -> Gdk.RGBA:
        if self.anime.get_is_favorite():
            return Gdk.RGBA(1, 1, 0, 1)
        else:
            return Gdk.RGBA(0, 0, 0, 1)

    def onclick(self, widget):
        self.anime.set_favorite(not self.anime.get_is_favorite())
        self.fav_icon.override_color(Gtk.StateFlags.NORMAL, self.get_fav_icon_color())
