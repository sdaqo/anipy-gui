import sys
import threading
from gi.repository import Gio, Gtk, Gdk, GLib
from loguru import logger

from anipy_cli import Entry, query, config
from anipy_gui.gui.sidebar import Sidebar, SidebarSection, SideBarRow
from anipy_gui.gui.widgets import AnimeGrid, AnimeWidget, AnimeView
from anipy_gui.gui.util import get_template_path, get_icon_path
from anipy_gui.anime import Anime


@Gtk.Template(filename=get_template_path("anipy-window.ui"))
class AniPyWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "anipywindow"

    anipy_logo: Gtk.Image = Gtk.Template.Child()
    main_stack: Gtk.Stack = Gtk.Template.Child()
    sidebar_container: Gtk.Viewport = Gtk.Template.Child()

    def __init__(self, application, *args, **kwargs):
        super().__init__(
            title="AnipyGUI",
            application=application,
            default_width=800,
            default_height=800,
            *args,
            **kwargs
        )

        self.application = application
        self.sidebar = Sidebar(application=application)
        self.sidebar.connect("row-selected", self.on_sidebar_row_selected)
        
        self.sidebar_container.get_style_context().add_class("sidebar-container")
        self.sidebar_container.add(self.sidebar)
        self.sidebar_container.show_all()

        self.anipy_logo.set_from_file(get_icon_path("anipy.ico"))

        self.search_anime_grid = AnimeView(application=application)
        self.main_stack.add_named(self.search_anime_grid, "anime_grid")



        self.main_stack.show_all()

        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_path(get_template_path("anipy-gui.css"))
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_sidebar_row_selected(self, widget, row: Gtk.ListBoxRow):
        filtered_row = None

        for sec in self.sidebar.sections.values():
            for i in sec.rows:
                if i.gtk_object == row:
                    filtered_row = i

        if not filtered_row:
            return

        if filtered_row.callback:
            filtered_row.callback()

    def search_anime(self, anime_query: str):
        GLib.idle_add(self.search_anime_grid.clear_grid)
        GLib.idle_add(self.search_anime_grid.start_loading)
        logger.debug("Starting search for {}", anime_query)
        query_cls = query(anime_query, Entry())
        links_n_names = query_cls.get_links()

        logger.debug("Found {}", links_n_names)
        if links_n_names == 0:
            GLib.idle_add(self.search_anime_grid.stop_loading)
            return
        
        widgets = []
        for l, n in zip(*links_n_names):
            gogo_url = config.Config().gogoanime_url
            anime = Anime(show_name=n, category_url=gogo_url+l)
            anime_widget = AnimeWidget(
                anime=anime,
                img_loader=anime.get_image
            )
            widgets.append(anime_widget)
        GLib.idle_add(self.search_anime_grid.stop_loading)

        for i in widgets:
            GLib.idle_add(self.search_anime_grid.add_anime_widget, i)

        GLib.idle_add(self.search_anime_grid.show_all)

    @Gtk.Template.Callback()
    def on_about(self, widget):
        about_dialog = Gtk.AboutDialog(transient_for=self, modal=True)
        about_dialog.present()

    @Gtk.Template.Callback()
    def on_search_key(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            search_thread = threading.Thread(target=self.search_anime, args=(widget.get_text(),))
            search_thread.daemon = True
            search_thread.start()


    @Gtk.Template.Callback()
    def on_quit(self, widget):
        self.application.quit()
