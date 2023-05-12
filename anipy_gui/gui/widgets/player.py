from typing import Union, Callable

from loguru import logger
from gi.repository import Gtk, Gdk
from mpv import MPV

from anipy_gui.anime import Anime
from anipy_gui.gui.util import KEYMAP, MODIFIER_KEYMAP, get_icon_path

#TODO here:
# build in custom key bindings for next episode, previous episode, etc.
# onscreen display to display helpful information
 

class MpvPlayer(Gtk.Window):
    def __init__(self, anime: Anime, on_close_cb: Callable[[], None]):
        super().__init__(
            title=anime.show_name, 
            default_width=1280, 
            default_height=720, 
        )
        self.anime = anime
        self.current_episode = -1
        self.on_close_cb = on_close_cb
        
        self.connect("destroy", self.on_destroy)
        self.connect("key-press-event", self.on_key_press_event)
        self.connect("key-release-event", self.on_key_release_event)
        self.set_icon_from_file(get_icon_path("anipy.ico"))

        wg = Gtk.Frame()
        wg.set_shadow_type(Gtk.ShadowType.NONE)
        
        spinner = Gtk.Spinner()
        wg.add(spinner)
        spinner.start()

        self.add(wg)
        self.show_all()

        self.mpv = MPV(
            wid=str(self.get_window().get_xid()), 
            input_default_bindings=True, 
            input_vo_keyboard=True, osc=True
        )

        self.mpv.observe_property("pause", self.on_pause)
        self.mpv.observe_property("fullscreen", self.on_fullscreen)

    def on_next_ep(self):
        ep_list = self.anime.get_episodes()
        
        #if episode + 1 == ep_list[-1]["ep"]:
        


    def on_prev_ep(self):
        ...

    def on_destroy(self, *args):
        self.anime.add_progress(self.current_episode, self.mpv.time_pos)
        self.mpv.terminate()
        self.on_close_cb()

    def on_pause(self, _name, value):
        logger.debug(self.mpv.time_pos)
        self.anime.add_progress(self.current_episode, self.mpv.time_pos)

    def on_fullscreen(self, _name, value):
        if value:
            self.fullscreen()
        else:
            self.unfullscreen()

    def on_key_press_event(self, widget, event: Gdk.EventKey):
        key = KEYMAP.get(event.keyval, event.string)
        modifier = MODIFIER_KEYMAP.get(event.state, None)

        if key:
            logger.debug(f"Key pressed: {key}")
            if modifier:
                key = f"{modifier}+{Gdk.keyval_name(event.keyval)}"
            self.mpv.keydown(key)

    def on_key_release_event(self, widget, event: Gdk.EventKey):
        key = KEYMAP.get(event.keyval, event.string)
        modifier = MODIFIER_KEYMAP.get(event.state, None)

        if key and self.mpv:
            logger.debug(f"Key released: {key}")
            if modifier:
                key = f"{modifier}+{Gdk.keyval_name(event.keyval)}"
            self.mpv.keyup(key)


    def play_episde(self, episode: Union[int, float], episode_link: str):
        if episode == self.current_episode:
            return
        self.current_episode = episode
        self.set_title(f"{self.anime.show_name} - Episode {episode}")
        progress = self.anime.get_progress_episode(self.current_episode)
        if progress is not None:
            progress = progress.time

        self.mpv.play(episode_link)
        self.mpv.wait_until_playing()
       
        if progress is not None:
            logger.debug(f"Seeking to {progress}")
            self.mpv.seek(progress)
