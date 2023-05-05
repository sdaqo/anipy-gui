from dataclasses import dataclass
from typing import Callable, Optional, List
from gi.repository import Gtk, Gdk, Pango


@dataclass(frozen=True)
class SideBarRow:
    title: str
    gtk_object: Gtk.ListBoxRow
    callback: Optional[Callable]


class SidebarSection:
    def __init__(self, title, header_icon: Gtk.Image):
        self.title = title
        self.header_icon = header_icon
        self.header_icon.get_style_context().add_class("icon")
        self.rows: List[SideBarRow] = []

        self._add_header()

    def add_button(
        self,
        title: str,
        callback: Callable,
        icon: Optional[Gtk.Image] = None,
        removeable: bool = False,
        remove_callback: Optional[Callable[[SideBarRow], None]] = None,
    ):
        row = Gtk.ListBoxRow()

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_margin_start(7)

        if icon:
            box.pack_start(icon, expand=False, fill=False, padding=4)
        else:
            box.pack_start(Gtk.Image(), expand=False, fill=False, padding=4)

        label = Gtk.Label(hexpand=False, halign=Gtk.Align.START, label=title)
        label.set_max_width_chars(27)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        box.pack_start(label, expand=True, fill=True, padding=0)

        row.get_style_context().add_class("sidebar-button")
        row.add(box)

        sidebar_row = SideBarRow(title, row, callback)

        remove_btn = Gtk.Button()
        remove_btn.set_relief(Gtk.ReliefStyle.NONE)
        remove_btn.set_focus_on_click(False)
        remove_btn.set_can_focus(False)
        remove_btn.set_can_default(False)
        remove_btn.set_always_show_image(True)
        if removeable:
            remove_btn.set_image(
                Gtk.Image.new_from_icon_name(
                    "edit-clear-all-symbolic", Gtk.IconSize.BUTTON
                )
            )
            remove_btn.connect("clicked", lambda _: remove_callback(sidebar_row))
        else:
            placholder_icon = Gtk.Image.new_from_icon_name(
                "edit-clear-all-symbolic", Gtk.IconSize.BUTTON
            )
            placholder_icon.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 0))

            remove_btn.set_image(placholder_icon)
            remove_btn.set_sensitive(False)
        box.pack_end(remove_btn, expand=False, fill=False, padding=0)

        self.rows.append(sidebar_row)

        return sidebar_row

    def _add_header(self):
        row = Gtk.ListBoxRow()
        row.set_activatable(False)
        row.set_selectable(False)

        outer_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
        )
        outer_box.set_size_request(200, -1)

        inner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        inner_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        inner_box.set_margin_top(6)
        inner_box.set_margin_bottom(6)
        inner_box.set_margin_start(9)
        inner_box.set_margin_end(9)

        label = Gtk.Label(
            use_markup=True,
            halign=Gtk.Align.START,
            label=f"<span size='12000'><b>{self.title}</b></span>",
        )
        label.get_style_context().add_class("dim-label")

        inner_box.pack_start(label, expand=True, fill=True, padding=0)
        inner_box.pack_end(self.header_icon, expand=False, fill=False, padding=0)

        sep = Gtk.HSeparator()
        sep.get_style_context().add_class("sidebar-separator")

        outer_box.pack_start(inner_box, expand=False, fill=False, padding=0)
        outer_box.pack_start(sep, expand=False, fill=True, padding=0)

        row.add(outer_box)
        self.rows.append(SideBarRow(self.title, row, None))


class Sidebar(Gtk.ListBox):
    def __init__(self, application: Gtk.Application):
        super().__init__()
        self.set_size_request(200, -1)
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.get_style_context().add_class("sidebar")

        self.application = application
        self.sections: dict[str, SidebarSection] = {}
        self._init_sections()

    def _init_sections(self):
        search_section = SidebarSection(
            title="Search",
            header_icon=Gtk.Image.new_from_icon_name(
                "system-search-symbolic", Gtk.IconSize.LARGE_TOOLBAR
            ),
        )

        user_section = SidebarSection(
            title="User",
            header_icon=Gtk.Image.new_from_icon_name(
                "user-available-symbolic", Gtk.IconSize.LARGE_TOOLBAR
            ),
        )

        anime_section = SidebarSection(
            title="Anime",
            header_icon=Gtk.Image.new_from_icon_name(
                "applications-multimedia-symbolic", Gtk.IconSize.LARGE_TOOLBAR
            ),
        )

        self.sections["Search"] = search_section
        self.sections["User"] = user_section
        self.sections["Anime"] = anime_section

        self.reload()

    def reload(self):
        self.foreach(lambda x: self.remove(x))

        for sec in self.sections.values():
            for row in sec.rows:
                self.add(row.gtk_object)

    def add_section(
        self, section_name: str, section_title: str, header_icon: Gtk.Image
    ) -> SidebarSection:
        new_section = SidebarSection(title=section_title, header_icon=header_icon)
        self.sections[section_name] = new_section
        self.reload()
        self.show_all()

        return new_section

    def add_button(
        self,
        section_name: str,
        title: str,
        callback: Callable,
        icon: Optional[Gtk.Image] = None,
        removeable: bool = False,
        remove_callback: Optional[Callable[[SideBarRow], None]] = None,
    ) -> SideBarRow:
        btn = self.sections[section_name].add_button(
            title, callback, icon, removeable, remove_callback
        )
        self.reload()
        self.show_all()

        return btn

    def remove_button(self, sidebar_row_button: SideBarRow):
        for sec in self.sections.values():
            for row in sec.rows:
                if row == sidebar_row_button:
                    sec.rows.remove(row)

        self.remove(sidebar_row_button.gtk_object)

    def select_row_by_title(self, title: str):
        for sec in self.sections.values():
            for row in sec.rows:
                if row.title == title:
                    self.select_row(row.gtk_object)
