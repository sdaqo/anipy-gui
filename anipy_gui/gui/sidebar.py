from dataclasses import dataclass
from typing import Callable, Optional, List
from gi.repository import GLib, Gio, Gtk


@dataclass(frozen=True)
class SideBarRow:
    title: str
    gtk_object: Gtk.ListBoxRow
    callback: Optional[Callable]


class SidebarSection:
    def __init__(self, title, header_icon: Gtk.Image):
        self.title = title
        self.header_icon = header_icon
        self.rows: List[SideBarRow] = []

        self._add_header()

    def add_button(
        self, title: str, callback: Callable, icon: Optional[Gtk.Image] = None
    ):
        row = Gtk.ListBoxRow()

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_margin_start(7)

        label = Gtk.Label(hexpand=False, halign=Gtk.Align.START, label=title)
        box.add(label)

        if icon:
            box.add(icon)

        row.add(box)

        sidebar_row = SideBarRow(title, row, callback)
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

        sep = Gtk.Separator()

        outer_box.add(inner_box)
        outer_box.add(sep)

        row.add(outer_box)
        self.rows.append(SideBarRow(self.title, row, None))


class Sidebar(Gtk.ListBox):
    def __init__(self, application: Gtk.Application):
        super().__init__()
        self.set_size_request(200, -1)
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)

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
                "user-idle-symbolic", Gtk.IconSize.LARGE_TOOLBAR
            ),
        )

        player_section = SidebarSection(
            title="Players",
            header_icon=Gtk.Image.new_from_icon_name(
                "applications-multimedia-symbolic", Gtk.IconSize.LARGE_TOOLBAR
            ),
        )

        self.sections["Search"] = search_section
        self.sections["User"] = user_section
        self.sections["Players"] = player_section

        for sec in self.sections.values():
            for row in sec.rows:
                self.add(row.gtk_object)

    def add_section(
        self, section_name: str, section_title: str, header_icon: Gtk.Image
    ) -> SidebarSection:
        new_section = SidebarSection(title=section_title, header_icon=header_icon)
        self.sections[section_name] = new_section

        return new_section

    def add_button(
        self,
        section_name: str,
        title: str,
        callback: Callable,
        icon: Optional[Gtk.Image] = None,
    ) -> SideBarRow:
        btn = self.sections[section_name].add_button(title, callback, icon)
        self.add(btn.gtk_object)

        return btn

    def remove_button(self, sidebar_row_button: SideBarRow):
        self.remove(sidebar_row_button.gtk_object)
