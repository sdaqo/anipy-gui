from loguru import logger

from mpv import MPV, MpvRenderContext, MpvGlGetProcAddressFn
from gi.repository import Gtk, Gdk, GLib


from OpenGL import GL, GLX
import ctypes
from anipy_gui.gui.util import KEYMAP, MODIFIER_KEYMAP, MOUSE_BUTTON_MAP


def get_process_address(_, name):
    address = GLX.glXGetProcAddress(name.decode("utf-8"))
    return ctypes.cast(address, ctypes.c_void_p).value

class MpvPlayer(Gtk.Frame):
    def __init__(self):
        super().__init__()
        self.set_can_focus(True)
        self.set_shadow_type(Gtk.ShadowType.NONE)
        self.area = MpvOpenGlArea()
        self.add(self.area)
        
        self.connect("key-press-event", self.on_key_press_event)
        self.connect("key-release-event", self.on_key_release_event)
        
        self.show_all()

    def play(self, url):
        self.area.play(url)


    def on_key_press_event(self, widget, event: Gdk.EventKey):
        key = KEYMAP.get(event.keyval, event.string)
        modifier = MODIFIER_KEYMAP.get(event.state, None)

        if key and self.area.mpv:
            logger.debug(f"Key pressed: {key}")
            if modifier:
                key = f"{modifier}+{Gdk.keyval_name(event.keyval)}"
            self.area.mpv.keydown(key)

    def on_key_release_event(self, widget, event: Gdk.EventKey):
        key = KEYMAP.get(event.keyval, event.string)
        modifier = MODIFIER_KEYMAP.get(event.state, None)

        if key and self.area.mpv:
            logger.debug(f"Key released: {key}")
            if modifier:
                key = f"{modifier}+{Gdk.keyval_name(event.keyval)}"
            self.area.mpv.keyup(key)

class MpvOpenGlArea(Gtk.GLArea):

    def __init__(self, **properties):
        super().__init__(**properties)
        self.set_auto_render(False)

        self._proc_addr_wrapper = MpvGlGetProcAddressFn(get_process_address)

        self.ctx = None
        self.mpv = MPV(
            vo="libmpv",
            input_default_bindings=True, 
            input_vo_keyboard=True,
            osc=True,
        )

        self.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.SCROLL_MASK
        )
        self.connect("realize", self.on_realize)
        self.connect("render", self.on_render)
        self.connect("unrealize", self.on_unrealize)
        self.connect("motion-notify-event", self.on_motion_notify_event)
        self.connect("button-press-event", self.on_button_press_event)
        self.connect("scroll-event", self.on_scroll_event)


    def on_realize(self, area):
        self.make_current()
        self.ctx = MpvRenderContext(self.mpv, 'opengl',
                                    opengl_init_params={'get_proc_address': MpvGlGetProcAddressFn(get_process_address)})
        self.ctx.update_cb = self.wrapped_c_render_func

    def on_unrealize(self, arg):
        #TODO: maybe hint?: https://github.com/mpv-player/mpv/blob/6234a709202282d8a8bfffd0ee4f9d80561dd4b9/player/client.c#LL191C49-L191C49
        #self.disconnect_by_func(self.on_render)
        self.ctx.free()
        self.mpv.terminate()
        self.mpv.wait_for_shutdown()
        logger.debug("Mpv terminated")

    def wrapped_c_render_func(self):
        GLib.idle_add(self.call_frame_ready, None, GLib.PRIORITY_HIGH)

    def call_frame_ready(self, *args):
        if self.ctx.update():
            self.queue_render()

    def on_render(self, arg1, arg2):
        if self.ctx:
            factor = self.get_scale_factor()
            rect = self.get_allocated_size()[0]

            width = rect.width * factor
            height = rect.height * factor

            fbo = GL.glGetIntegerv(GL.GL_DRAW_FRAMEBUFFER_BINDING)
            self.ctx.render(flip_y=True, opengl_fbo={'w': width, 'h': height, 'fbo': fbo})
            return True
        return False

    def play(self, media):
        self.mpv.play(media)

    def on_motion_notify_event(self, widget, event: Gdk.EventMotion):
        self._send_mpv_mouse(event)
        return True
    
    def on_button_press_event(self, widget, event: Gdk.EventButton):
        state = MOUSE_BUTTON_MAP.get(event.button, None)

        if state is None:
            return False

        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            mode = 'double'
        else:
            mode = 'single'

        self._send_mpv_mouse(event, state, mode)
        return True
    
    def on_scroll_event(self, widget, event: Gdk.EventScroll):
        direction = 3 if int(event.direction) == 0 else 4
        
        self._send_mpv_mouse(event, direction, 'single')
        return True

    def _send_mpv_mouse(self, event, *args):
        self.mpv.command('mouse', int(event.x), int(event.y), *args)



