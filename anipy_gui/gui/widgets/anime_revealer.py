from gi.repository import GLib, Gio, Gtk, GdkPixbuf, Pango, Gdk


class AnimeRevealer(Gtk.Revealer):
    def __init__(self):
        super().__init__()
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self.set_transition_duration(1000)

        self.container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.anime_label = Gtk.Label()

        self.play_button = Gtk.Button()
        self.play_button.set_image(
            Gtk.Image.new_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
        )
        self.play_button.set_always_show_image(True)
        self.play_button.set_relief(Gtk.ReliefStyle.NONE)
        self.play_button.set_focus_on_click(False)

        self.favorite_button = Gtk.Button()
        self.favorite_button.set_image(
            Gtk.Image.new_from_icon_name("emblem-favorite", Gtk.IconSize.BUTTON)
        )
        self.favorite_button.set_always_show_image(True)
        self.favorite_button.set_relief(Gtk.ReliefStyle.NONE)
        self.favorite_button.set_focus_on_click(False)

        self.container.pack_start(self.anime_label, True, True, 0)
