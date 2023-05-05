from gi.repository import Gtk


class SpinnerButton(Gtk.Button):
    def __init__(self, label: str, image: Gtk.Image):
        super().__init__()
        self.image = image
        self.label = label
        self.inner_box = Gtk.Box()
        self.inner_box.add(self.image)
        self.inner_box.add(Gtk.Label(self.label))

        self.add(self.inner_box)
        self.set_always_show_image(True)

        self.spinner = Gtk.Spinner()
    
    def start_spinner(self):
        self.remove(self.inner_box)
        self.add(self.spinner)
        self.spinner.start()
        self.show_all()

    def stop_spinner(self):
        self.spinner.stop()
        self.remove(self.spinner)
        self.add(self.inner_box)
        self.show_all()


