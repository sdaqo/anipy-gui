import webbrowser
from pathlib import Path
from typing import Callable
from gi.repository import Gdk, Gtk


def get_template_path(template_name: str) -> str:
    directory = Path(__file__).parent / "templates"
    return str(directory / template_name)


def get_icon_path(icon_name: str) -> str:
    directory = Path(__file__).parent / "images"
    return str(directory / icon_name)

def open_link(link: str):
    webbrowser.open(link)

KEYMAP = {
    Gdk.KEY_space: "space",
    Gdk.KEY_Up: "up",
    Gdk.KEY_Down: "down",
    Gdk.KEY_Left: "left",
    Gdk.KEY_Right: "right",
    Gdk.KEY_Return: "enter",
    Gdk.KEY_Escape: "esc",
    Gdk.KEY_BackSpace: "bs",
    Gdk.KEY_Delete: "del",
    Gdk.KEY_Tab: "tab",
    Gdk.KEY_F1: "F1",
    Gdk.KEY_F2: "F2",
    Gdk.KEY_F3: "F3",
    Gdk.KEY_F4: "F4",
    Gdk.KEY_F5: "F5",
    Gdk.KEY_F6: "F6",
    Gdk.KEY_F7: "F7",
    Gdk.KEY_F8: "F8",
    Gdk.KEY_F9: "F9",
    Gdk.KEY_F10: "F10",
    Gdk.KEY_F11: "F11",
    Gdk.KEY_F12: "F12",
}

MODIFIER_KEYMAP = {
    Gdk.ModifierType.CONTROL_MASK: "ctrl",
    Gdk.ModifierType.MOD1_MASK: "alt",
    Gdk.ModifierType.SUPER_MASK: "meta",
    Gdk.ModifierType.MOD4_MASK: "meta",
}

MOUSE_BUTTON_MAP = {
    Gdk.BUTTON_PRIMARY: 0, 
    Gdk.BUTTON_SECONDARY: 2,
    Gdk.BUTTON_MIDDLE: 1,
}
