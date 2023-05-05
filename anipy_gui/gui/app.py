import sys
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from pathlib import Path
from loguru import logger

from anipy_gui.gui.anipywindow import AniPyWindow


class AniPyApplication(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.sdaqo.anipy-gui",
        )

        self.window = None

    def do_activate(self) -> None:
        if not self.window:
            self.window = AniPyWindow(application=self)

        self.window.present()

    def quit(self, **kwargs):
        Gtk.Application.quit(self)


if __name__ == "__main__":
    app = AniPyApplication()
    app.run(sys.argv)
