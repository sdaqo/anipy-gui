from gi.repository import Gtk, Gdk
from loguru import logger

from anipy_gui.gui.widgets.favorites import FavoritesView
from anipy_gui.gui.widgets.sidebar import Sidebar, SideBarRow
from anipy_gui.gui.widgets import AnimeSearchWidget
from anipy_gui.gui.widgets.anime_tab import AnimeTabView
from anipy_gui.gui.util import get_template_path, get_icon_path
from anipy_gui.gui.widgets.anime_revealer import RevealerAction
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
            default_width=1200,
            default_height=800,
            *args,
            **kwargs,
        )

        self.application = application
        self.sidebar = Sidebar(application=application)
        self.sidebar.connect("row-selected", self.on_sidebar_row_selected)

        self.sidebar_container.get_style_context().add_class("sidebar-container")
        self.sidebar_container.add(self.sidebar)
        self.sidebar_container.show_all()

        self.anipy_logo.set_from_file(get_icon_path("anipy.ico"))

        self.search_widget_revealer_actions = [
            RevealerAction(
                "Play",
                self.on_anime_play,
                icon_name="media-playback-start-symbolic",
            ),
        ]

        self.search_anime_widget_default = AnimeSearchWidget(
            application=application,
            revealer_actions=self.search_widget_revealer_actions,
        )
        self.main_stack.add_named(self.search_anime_widget_default, "dafault_search")
        self.sidebar.add_button(
            "Search",
            "Default Search",
            lambda: self.main_stack.set_visible_child(self.search_anime_widget_default),
            icon=Gtk.Image.new_from_icon_name(
                "system-search-symbolic", Gtk.IconSize.MENU
            ),
        )

        self.favorite_widget = FavoritesView(
            application=application,
            revealer_actions=self.search_widget_revealer_actions,
        )
        self.main_stack.add_named(self.favorite_widget, "favorites")

        def show_favorites_widget():
            self.main_stack.set_visible_child(self.favorite_widget)
            self.favorite_widget.load_favorite_animes()

        self.sidebar.add_button(
            "User",
            "Favorites",
            show_favorites_widget,
            icon=Gtk.Image.new_from_icon_name("starred-symbolic", Gtk.IconSize.MENU),
        )

        self.main_stack.show_all()

        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_path(get_template_path("anipy-gui.css"))
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # TESTING
        #self.on_anime_play(
        #    Anime("K-ON!", "https://gogoanime.gg/category/k-on")
        #)

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

    def on_anime_play(self, anime: Anime):
        if self.main_stack.get_child_by_name(anime.show_name):
            self.sidebar.select_row_by_title(anime.show_name)
            return

        anime_wg = AnimeTabView(anime=anime)
        self.main_stack.add_named(anime_wg, anime.show_name)
        
        def remove_anime(row: SideBarRow):
            anime_wg.destroy()
            self.sidebar.remove_button(row)

        self.sidebar.add_button(
            "Anime",
            anime.show_name,
            lambda: self.main_stack.set_visible_child(anime_wg),
            removeable=True,
            remove_callback=remove_anime
        )

        self.sidebar.select_row_by_title(anime.show_name)

        logger.debug("Play {}", anime)

    @Gtk.Template.Callback()
    def on_about(self, widget):
        about_dialog = Gtk.AboutDialog(transient_for=self, modal=True)
        about_dialog.present()

    @Gtk.Template.Callback()
    def on_search_key(self, widget, event):
        search_query = widget.get_text()

        def open_new_search():
            if self.main_stack.get_child_by_name(search_query):
                self.sidebar.select_row_by_title(f"Search: {search_query}")
                return

            search_wg = AnimeSearchWidget(
                application=self.application,
                revealer_actions=self.search_widget_revealer_actions,
            )
            self.main_stack.add_named(search_wg, search_query)

            def remove_search(row: SideBarRow):
                self.main_stack.remove(self.main_stack.get_child_by_name(search_query))
                self.sidebar.remove_button(row)

            sbar_button = self.sidebar.add_button(
                "Search",
                f"Search: {search_query}",
                lambda: self.main_stack.set_visible_child(search_wg),
                removeable=True,
                remove_callback=remove_search,
            )

            search_wg.start_search(search_query)
            search_wg.show_all()

            self.sidebar.select_row(sbar_button.gtk_object)

        if (
            event.keyval == Gdk.KEY_Return
            and event.state == Gdk.ModifierType.CONTROL_MASK
        ):
            open_new_search()
        elif event.keyval == Gdk.KEY_Return:
            curr_name = self.main_stack.get_visible_child_name()
            curr_child = self.main_stack.get_visible_child()
            if isinstance(curr_child, AnimeSearchWidget):
                if curr_child.searching:
                    open_new_search()
                elif not self.search_anime_widget_default.searching:
                    self.search_anime_widget_default.start_search(search_query)
                    self.sidebar.select_row_by_title("Default Search")
                elif curr_name == search_query:
                    curr_child.start_search(search_query)
                else:
                    open_new_search()
            else:
                open_new_search()

    @Gtk.Template.Callback()
    def on_quit(self, widget):
        self.application.quit()
