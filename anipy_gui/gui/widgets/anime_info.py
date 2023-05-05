from math import ceil
from re import I
from PIL import Image, ImageFilter
from gi.repository import Gtk, GLib, GdkPixbuf, GObject
from typing import Callable
from threading import Thread
from loguru import logger
from mpv import StreamReadFn


from anipy_gui.gui.widgets.anime_view import AnimeWidget
from anipy_gui.gui.util import open_link
from anipy_gui.gui.widgets.spinner_btn import SpinnerButton
from anipy_gui.anime import Anime

# IDEAS:
#   - Continue Button
#   - Indicator for last watched
#   - Mark already watched episodes

class ResizeableOverlay(Gtk.Overlay):
    def do_get_preferred_width(self):
        return (1, 1)



class AnimeInfoView(Gtk.Box):
    __gsignals__ = {
            'episodes-loaded': (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_PYOBJECT, ))
    }
    
    def __init__(
        self, anime: Anime, play_cb: Callable[[int], None], dl_cb: Callable[[int], None]
    ):
        super().__init__()
        self.anime = anime
        self.play_cb = play_cb
        self.dl_cb = dl_cb

        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.spinner = Gtk.Spinner()

        self.header = ResizeableOverlay()
        self.header.set_valign(Gtk.Align.START)
    
        self.overlay_box = Gtk.Box()
        self.overlay_box.set_valign(Gtk.Align.START)
        self.overlay_box.set_halign(Gtk.Align.START)
        self.overlay_box.set_margin_start(10)
        self.overlay_box.set_margin_top(10)
        #self.overlay_box.set_margin_end(10)
        
        self.header_anime_wg = AnimeWidget(self.anime, self.anime.get_image, 180, 270)
        self.header_anime_wg.set_valign(Gtk.Align.START)
        self.header_anime_wg.set_halign(Gtk.Align.START)

        self.overlay_box.add(self.header_anime_wg)
        
        self.anime_info = Gtk.Box()
        self.overlay_box.add(self.anime_info)

        self.header_bg = Gtk.Image()

        self.header.add(self.header_bg)
        self.header.add_overlay(self.overlay_box)

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_hexpand(True)
        self.scroll.set_vexpand(True)

        self.viewport = Gtk.Viewport()
        self.viewport.set_hexpand(True)
        self.viewport.set_vexpand(True)
        self.viewport.set_shadow_type(Gtk.ShadowType.NONE)
        self.scroll.add(self.viewport)


        self.episode_grid = Gtk.Grid()
        self.episode_grid.set_hexpand(True)
        self.episode_grid.set_vexpand(True)
        self.episode_grid.set_halign(Gtk.Align.FILL)
        self.episode_grid.set_valign(Gtk.Align.START)
        self.episode_grid.set_margin_start(10)
        self.episode_grid.set_margin_top(10)
        self.episode_grid.set_margin_end(10)
        self.episode_grid.set_margin_bottom(10)
        self.episode_grid.set_column_spacing(10)
        self.episode_grid.set_row_spacing(10)
            
        self.viewport.add(self.episode_grid)

        self.add(self.header)
        self.add(self.scroll)

        self.width = 0
        self.header_height = 300
        self.allocation_timeout_id = None

        self.bg_image_thread = Thread(target=self._set_header_img)
        self.bg_image_thread.start()

        self.anime_info_thread = Thread(target=self._set_anime_info)
        self.anime_info_thread.start()
        
        self.connect("episodes-loaded", self._set_episodes)
        self.episode_thread = Thread(target=self._load_episodes)
        self.episode_thread.start()
        
        self.connect("size-allocate", self.on_size_allocate)

    def _set_header_img(self):
        w, h = self.get_allocated_width(), self.header_height
        img = self.anime.get_image()
        img = Image.open(img)
        ar = img.height / img.width
        img = img.resize((w, ceil(w*ar)), Image.ANTIALIAS)
        upper = (img.height // 2) - (h // 2)
        img = img.crop((0, upper, img.width, upper + h))
        img = img.filter(ImageFilter.GaussianBlur(20))
        img = img.convert("RGB")

        img = GdkPixbuf.Pixbuf.new_from_bytes(
            GLib.Bytes.new(img.tobytes()), GdkPixbuf.Colorspace.RGB, False, 8, img.width, img.height, img.width * 3
        )
        

        self.header_bg.set_from_pixbuf(img)
        self.header.show_all()
    
    def _set_anime_info(self):
        info = self.anime.get_anime_info()
        
        inner_box = Gtk.Box()
        inner_box.get_style_context().add_class("anime-info")
        inner_box.set_orientation(Gtk.Orientation.VERTICAL)
        inner_box.set_margin_end(10)

        def add_label(text):
            label = Gtk.Label()
            label.set_markup(text)
            label.set_line_wrap(True)
            label.set_halign(Gtk.Align.START)
            inner_box.pack_start(label, False, True, 0)

        add_label(f"<b>Genres:</b> {', '.join(info.genres)}")
        add_label(f"<b>Type:</b> {info.type}")
        add_label(f"<b>Release Year:</b> {info.release_year}")
        add_label(f"<b>Status:</b> {info.status}")

        ext_link = Gtk.LinkButton.new_with_label("Gogoanime")
        ext_link.get_style_context().add_class("no-padding")
        ext_link.set_halign(Gtk.Align.START)
        ext_link.connect("activate-link", lambda _: open_link(self.anime.category_url))
        ext_link.set_can_focus(False)

        inner_box.pack_start(ext_link, False, True, 0)
        
        synopsis = info.synopsis
        if len(synopsis) > 500:
            synopsis = synopsis[:500]
            synopsis = synopsis[:synopsis.rfind(" ")]
            synopsis += "..."
        
        synopsis_box = Gtk.Box()
        synopsis_box.set_orientation(Gtk.Orientation.VERTICAL)
        synopsis_label = Gtk.Label()
        synopsis_label.set_markup(f"<b>Synopsis:</b> {synopsis}")
        synopsis_label.set_justify(Gtk.Justification.FILL)
        synopsis_label.set_line_wrap(True)
        synopsis_label.set_margin_start(10)
        synopsis_label.set_margin_end(10)
        synopsis_label.set_max_width_chars(50)
        
        full_synopsis_dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Synopsis",
        )
        full_synopsis_dialog.format_secondary_text(info.synopsis)

        full_synopsis_button = Gtk.LinkButton()
        full_synopsis_button.set_label("Read More")
        full_synopsis_button.set_can_focus(False)
        def on_activate_link(_):
            full_synopsis_dialog.run()
            full_synopsis_dialog.hide()
            return True
        full_synopsis_button.connect("activate-link", on_activate_link)

        synopsis_box.add(synopsis_label)
        synopsis_box.add(full_synopsis_button)
                
        GLib.idle_add(self.anime_info.pack_start, synopsis_box, True, True, 0)
        GLib.idle_add(self.anime_info.pack_end, inner_box, True, True, 0)
        GLib.idle_add(self.anime_info.show_all)
    
    def _load_episodes(self):
        spinner = Gtk.Spinner()
        spinner.start()
        GLib.idle_add(self.episode_grid.add, spinner)
        GLib.idle_add(self.episode_grid.show_all)
        episodes = self.anime.get_episodes()
        GLib.idle_add(self.episode_grid.remove, spinner)
        GLib.idle_add(self.emit, "episodes-loaded", episodes)
    
    def _set_episodes(self, wg, episodes):
        max_cols = 2
        col = 0
        row = 0
        for ep in episodes:
            logger.debug(f"Adding episode {ep['ep']}")
            episode_box = Gtk.Box()
            episode_box.set_hexpand(True)
            episode_box.get_style_context().add_class("episode-row")
            label = Gtk.Label()
            label.set_markup(f"<b>Episode {ep['ep']}</b>")
            label.set_halign(Gtk.Align.START)
            
            button_box = Gtk.Box()
            button_box.set_halign(Gtk.Align.END)
            button_box.set_hexpand(True)
            
            play_button = SpinnerButton(
                "Play", Gtk.Image.new_from_icon_name("media-playback-start-symbolic", Gtk.IconSize.BUTTON)
            )
            play_button.set_relief(Gtk.ReliefStyle.NONE)
            play_button.set_can_focus(False)
            play_button.connect("clicked", self.play_cb, ep["ep"])

            download_button = SpinnerButton(
                "Download", Gtk.Image.new_from_icon_name("document-save-symbolic", Gtk.IconSize.BUTTON)
            )
                
            download_button.set_can_focus(False)
            download_button.set_relief(Gtk.ReliefStyle.NONE)
            download_button.connect("clicked", self.dl_cb, ep["ep"])
            
            button_box.pack_start(play_button, False, True, 0)
            button_box.pack_start(download_button, False, True, 0)

            episode_box.pack_start(label, True, True, 0)
            episode_box.pack_end(button_box, False, True, 0)
            self.episode_grid.attach(episode_box, col, row, 1, 1)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1
            
        self.episode_grid.show_all()

    def _on_size_allocate(self, widget, allocation):
        alloc_w = allocation.width
        if alloc_w == self.width or alloc_w == 1:
           return

        if self.bg_image_thread.is_alive():
            self.bg_image_thread.join()
        self.bg_image_thread = Thread(target=self._set_header_img)
        self.bg_image_thread.start()
        self.width = allocation.width

    def on_size_allocate(self, widget, allocation):
        if self.allocation_timeout_id is not None:
            GLib.source_remove(self.allocation_timeout_id)

        self.allocation_timeout_id = GLib.timeout_add(100, self._on_size_allocate, widget, allocation)
