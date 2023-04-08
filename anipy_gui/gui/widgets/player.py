#!/usr/bin/env python3
import gi

import mpv

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class MainClass(Gtk.Window):
    def __init__(self):
        super(MainClass, self).__init__()
        self.set_default_size(600, 400)
        self.connect("destroy", self.on_destroy)

        widget = Gtk.Frame()
        self.add(widget)
        self.show_all()

        # Must be created >after< the widget is shown, else property 'window' will be None
        self.mpv = mpv.MPV(
            wid=str(widget.get_property("window").get_xid()),
            input_default_bindings=True,
            input_vo_keyboard=True,
            osc=True,
        )
        self.mpv.play("test.mkv")

    def on_destroy(self, widget, data=None):
        self.mpv.terminate()
        Gtk.main_quit()


if __name__ == "__main__":
    # This is necessary since like Qt, Gtk stomps over the locale settings needed by libmpv.
    # Like with Qt, this needs to happen after importing Gtk but before creating the first mpv.MPV instance.
    import locale

    locale.setlocale(locale.LC_NUMERIC, "C")

    application = MainClass()

    Gtk.main()
