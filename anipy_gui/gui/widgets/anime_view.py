import threading
from anipy_cli import Entry
from gi.repository import GLib, Gio, Gtk, GdkPixbuf, Pango, Gdk
from loguru import logger
from typing import Callable
from pathlib import Path

from anipy_gui.anime import Anime
from anipy_gui.gui.widgets.anime_revealer import AnimeRevealer


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


class AnimeWidget(Gtk.Overlay):
    WIDTH = 150
    HEIGHT = 220

    def __init__(self, anime: Anime, img_loader: Callable[..., Path]):
        super().__init__()
        self.set_size_request(self.WIDTH, self.HEIGHT)
        self.anime = anime
        self.img_loader = img_loader

        self.spinner = Gtk.Spinner()
        self.image_thread = threading.Thread(target=self.load_image)
        self.image_thread.daemon = True
        self.image_thread.start()

        self.fav_button = FavoriteButton(self.anime)

        self.title_box = Gtk.Box()
        self.title_box.set_valign(Gtk.Align.END)
        self.title_box.set_halign(Gtk.Align.START)
        self.title_box.set_margin_start(5)
        self.title_box.set_margin_bottom(5)
        self.title_box.set_margin_end(5)
        self.title_box.override_background_color(
            Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 0.7)
        )
        self.title_box.get_style_context().add_class("title-box")

        self.label = Gtk.Label(anime.show_name)
        self.label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(255, 255, 255, 1))
        self.label.set_max_width_chars(20)
        self.label.set_margin_start(2)
        self.label.set_margin_end(2)
        self.label.set_margin_top(2)
        self.label.set_margin_bottom(2)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)

        self.title_box.add(self.label)

        self.add_overlay(self.fav_button)
        self.add_overlay(self.title_box)

    def load_image(self):
        GLib.idle_add(self.add, self.spinner)
        GLib.idle_add(self.spinner.start)

        self.img_path = str(self.img_loader())
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.img_path)
        pixbuf = self.scale_image(pixbuf, self.HEIGHT, self.WIDTH)
        self.img = Gtk.Image.new_from_pixbuf(pixbuf)
        GLib.idle_add(self.remove, self.spinner)
        GLib.idle_add(self.add, self.img)
        GLib.idle_add(self.img.show)

    def scale_image(self, pixbuf: GdkPixbuf.Pixbuf, height, width) -> GdkPixbuf.Pixbuf:
        ar = pixbuf.get_width() / pixbuf.get_height()
        new_width = int(height * ar)
        pixbuf = pixbuf.scale_simple(new_width, height, GdkPixbuf.InterpType.BILINEAR)
        if pixbuf.get_width() >= width and pixbuf.get_height() >= height:
            src_x = int(pixbuf.get_width() / 2 - width / 2)
            pixbuf = pixbuf.new_subpixbuf(src_x, 0, width, height)
        else:
            pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
        return pixbuf

    def resize(self, width, height):
        self.set_size_request(width, height)
        self.remove(self.img)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.img_path)
        pixbuf = self.scale_image(pixbuf, height, width)
        self.img = Gtk.Image.new_from_pixbuf(pixbuf)
        self.add(self.img)


class AnimeGrid(Gtk.FlowBox):
    def __init__(self, application, on_anime_selected: Callable[[Anime], None]):
        super().__init__()
        self.set_valign(Gtk.Align.START)
        self.set_halign(Gtk.Align.START)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_homogeneous(False)
        self.set_activate_on_single_click(True)
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.set_max_children_per_line(999)
        self.set_min_children_per_line(4)
        self.connect("child-activated", self.on_child_activated)
        self.set_row_spacing(7)
        self.set_column_spacing(7)
        self.get_style_context().add_class("flow-box")

        self.application = application
        self.on_anime_selected = on_anime_selected

    def add_anime_widget(self, anime_widget: AnimeWidget):
        self.add(anime_widget)

    def on_child_activated(self, widget, child):
        anime_widget = child.get_child()
        self.on_anime_selected(anime_widget.anime)

    def clear_grid(self):
        for child in self.get_children():
            self.remove(child)


class AnimeView(Gtk.Box):
    def __init__(self, application):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.get_style_context().add_class("anime-view")

        self.overlay = Gtk.Overlay()
        self.overlay.set_hexpand(True)
        self.overlay.set_vexpand(True)
        self.pack_start(self.overlay, True, True, 0)

        self.spinner = None

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_hexpand(True)
        self.scroll.set_vexpand(True)

        self.viewport = Gtk.Viewport()
        self.viewport.set_hexpand(True)
        self.viewport.set_vexpand(True)
        self.viewport.set_shadow_type(Gtk.ShadowType.NONE)
        self.scroll.add(self.viewport)

        self.anime_grid = AnimeGrid(application, self.on_anime_selected)
        self.viewport.add(self.anime_grid)

        self.overlay.add(self.scroll)

        self.revealer = AnimeRevealer(
            play_callback=self.anime_play, download_callback=self.anime_download
        )
        self.revealer.set_reveal_child(False)
        self.pack_end(self.revealer, False, False, 0)

    def start_loading(self):
        self.spinner = Gtk.Spinner()
        self.overlay.add_overlay(self.spinner)
        self.anime_grid.set_visible(False)
        self.spinner.set_visible(True)
        self.spinner.start()

    def stop_loading(self):
        self.spinner.stop()
        self.overlay.remove(self.spinner)
        self.anime_grid.set_visible(True)

    def add_anime_widget(self, anime_widget: AnimeWidget):
        self.anime_grid.add_anime_widget(anime_widget)

    def anime_play(self, anime: Anime):
        logger.info("Wants to play")

    def anime_download(self, anime: Anime):
        logger.info("Wants to download")

    def on_anime_selected(self, anime: Anime):
        logger.debug("Selected anime: {}", anime.show_name)
        self.revealer.set_anime(anime)

        if self.revealer.get_reveal_child():
            self.revealer.set_reveal_child(False)
            self.revealer.set_visible(False)

        self.revealer.set_visible(True)
        self.revealer.set_reveal_child(True)

    def clear_grid(self):
        self.revealer.set_reveal_child(False)
        self.anime_grid.clear_grid()
