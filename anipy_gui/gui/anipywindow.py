import sys
from gi.repository import GLib, Gio, Gtk, Gdk

from anipy_cli import Entry

from anipy_gui.gui.sidebar import Sidebar, SidebarSection, SideBarRow
from anipy_gui.gui.widgets import AnimeGrid, AnimeWidget
from anipy_gui.gui.util import get_template_path, get_icon_path



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
        
        self.sidebar_container.add(self.sidebar)
        self.sidebar_container.show_all()
        
        self.anipy_logo.set_from_file(get_icon_path("anipy.ico"))

        self.anime_grid = AnimeGrid(application=application)
        self.main_stack.add_named(self.anime_grid, "anime_grid")

        self.anime_grid.add_anime_widget(AnimeWidget(anime_entry=Entry(show_name="Hyoukasssssssssssssssss"), img="some.jpg"))
        self.anime_grid.add_anime_widget(AnimeWidget(anime_entry=Entry(show_name="Hyouka"), img="some.jpg"))
        self.anime_grid.add_anime_widget(AnimeWidget(anime_entry=Entry(show_name="Hyouka"), img="some.jpg"))
        self.anime_grid.add_anime_widget(AnimeWidget(anime_entry=Entry(show_name="Hyouka"), img="some.jpg"))
        self.anime_grid.add_anime_widget(AnimeWidget(anime_entry=Entry(show_name="Hyouka"), img="some.jpg"))
        self.anime_grid.add_anime_widget(AnimeWidget(anime_entry=Entry(show_name="Hyouka"), img="some.jpg"))
        self.anime_grid.add_anime_widget(AnimeWidget(anime_entry=Entry(show_name="Hyouka"), img="some.jpg"))
        self.anime_grid.add_anime_widget(AnimeWidget(anime_entry=Entry(show_name="Hyouka"), img="some.jpg"))
        self.anime_grid.add_anime_widget(AnimeWidget(anime_entry=Entry(show_name="Hyouka"), img="some.jpg"))
        self.anime_grid.add_anime_widget(AnimeWidget(anime_entry=Entry(show_name="Hyouka"), img="some.jpg"))
        self.anime_grid.add_anime_widget(AnimeWidget(anime_entry=Entry(show_name="Hyouka"), img="some.jpg"))
        self.main_stack.show_all()

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

    @Gtk.Template.Callback()
    def on_about(self, widget):
        about_dialog = Gtk.AboutDialog(transient_for=self, modal=True)
        about_dialog.present()

    @Gtk.Template.Callback()
    def on_search_key(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            # TODO: DO the search thingy
            print("Search")

    @Gtk.Template.Callback()
    def on_quit(self, widget):
        self.application.quit()
