from anipy_cli import Entry
from gi.repository import GLib, Gio, Gtk, GdkPixbuf, Pango, Gdk


class AnimeWidget(Gtk.Overlay):
    WIDTH  = 150
    HEIGHT = 200
    def __init__(self, anime_entry: Entry, img: str):
        super().__init__()
        self.set_size_request(self.WIDTH, self.HEIGHT)
        self.anime_entry = anime_entry
        self.img_path = img

        pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.img_path)
        pixbuf = self.scale_image(pixbuf, self.HEIGHT, self.WIDTH)

        self.img = Gtk.Image.new_from_pixbuf(pixbuf)
        self.img.connect("button-press-event", self.onclick_img)
        self.add(self.img)

        self.fav_button = Gtk.Button()
        fav_icon = Gtk.Image.new_from_icon_name("starred-symbolic", Gtk.IconSize.BUTTON)

        # TODO: Make the color of the star change when the anime is favorited
        fav_icon.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 0, 1))
        self.fav_button.add(fav_icon)

        self.fav_button.add(fav_icon)
        self.fav_button.set_relief(Gtk.ReliefStyle.NONE)
        self.fav_button.set_valign(Gtk.Align.START)
        self.fav_button.set_halign(Gtk.Align.END)
        self.fav_button.set_margin_top(5)
        self.fav_button.set_margin_end(5)
        self.fav_button.connect("clicked", self.onclick_fav)
        self.fav_button.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 0.5))


        self.title_box = Gtk.Box()
        self.title_box.set_valign(Gtk.Align.END)
        self.title_box.set_halign(Gtk.Align.START)
        self.title_box.set_margin_start(5)
        self.title_box.set_margin_bottom(5)
        self.title_box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 0.7))
        #TODO: Rounded corners

        self.label = Gtk.Label(anime_entry.show_name)
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
    
    def scale_image(self, pixbuf: GdkPixbuf.Pixbuf, height, width) -> GdkPixbuf.Pixbuf:
        ar = pixbuf.get_width() / pixbuf.get_height()
        new_width  = int(height * ar)
        pixbuf = pixbuf.scale_simple(new_width, height, GdkPixbuf.InterpType.BILINEAR)
        if pixbuf.get_width() >= width or pixbuf.get_height() >= height:
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
        self.img.connect("button-press-event", self.onclick_img)
        self.add(self.img)

    def onclick_img(self, widget, event):
        ...

    def onclick_fav(self, widget, event):
        ...


class AnimeGrid(Gtk.FlowBox):
    def __init__(self, application):
        super().__init__() 
        self.set_valign(Gtk.Align.START)
        self.set_halign(Gtk.Align.START)
        self.set_homogeneous(True)
        self.set_activate_on_single_click(True)
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.set_max_children_per_line(10)
        self.set_min_children_per_line(4)

    def add_anime_widget(self, anime_widget: AnimeWidget):
        #anime_widget.resize(150, 200)
        self.add(anime_widget)

