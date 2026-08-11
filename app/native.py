from __future__ import annotations

import ctypes
import sys


def apply_topmost(widget) -> None:
    try:
        from PySide6.QtGui import QGuiApplication
        if QGuiApplication.platformName().lower() == "offscreen":
            return
        if sys.platform == "win32":
            _apply_windows(int(widget.winId()))
        elif sys.platform == "darwin":
            _apply_macos(int(widget.winId()))
    except Exception:
        pass


def _apply_windows(hwnd: int) -> None:
    user32 = ctypes.windll.user32
    GWL_EXSTYLE = -20
    flags = 0x00000020 | 0x08000000 | 0x00000080 | 0x00080000

    get_long = getattr(user32, "GetWindowLongPtrW", None) or user32.GetWindowLongW
    set_long = getattr(user32, "SetWindowLongPtrW", None) or user32.SetWindowLongW
    get_long.restype = ctypes.c_long
    get_long.argtypes = [ctypes.c_void_p, ctypes.c_int]
    set_long.restype = ctypes.c_long
    set_long.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_long]

    ex_style = get_long(hwnd, GWL_EXSTYLE)
    set_long(hwnd, GWL_EXSTYLE, ex_style | flags)

    HWND_TOPMOST = -1
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040
    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                        SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE | SWP_SHOWWINDOW)


_NS_SCREEN_SAVER_LEVEL = 1000
_NS_CAN_JOIN_ALL_SPACES = 1 << 0
_NS_STATIONARY = 1 << 2
_NS_IGNORES_CYCLE = 1 << 3
_NS_FULLSCREEN_AUXILIARY = 1 << 8


def _libobjc():
    return ctypes.CDLL("/usr/lib/libobjc.dylib")


def _sel(name: str):
    lib = _libobjc()
    f = lib.sel_registerName
    f.restype = ctypes.c_void_p
    f.argtypes = [ctypes.c_char_p]
    return f(name.encode())


def _msg(obj, selname: str):
    f = _libobjc().objc_msgSend
    f.restype = ctypes.c_void_p
    f.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    return f(obj, _sel(selname))


def _msg_i(obj, selname: str, value: int):
    f = _libobjc().objc_msgSend
    f.restype = ctypes.c_void_p
    f.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long]
    return f(obj, _sel(selname), ctypes.c_long(value))


def _msg_u(obj, selname: str, value: int):
    f = _libobjc().objc_msgSend
    f.restype = ctypes.c_void_p
    f.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
    return f(obj, _sel(selname), ctypes.c_ulong(value))


def _msg_b(obj, selname: str, value: bool):
    f = _libobjc().objc_msgSend
    f.restype = ctypes.c_void_p
    f.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool]
    return f(obj, _sel(selname), ctypes.c_bool(value))


def _apply_macos(win_id: int) -> None:
    view = ctypes.c_void_p(win_id)
    ns_window = _msg(view, "window")
    if not ns_window:
        return
    _msg_i(ns_window, "setLevel:", _NS_SCREEN_SAVER_LEVEL)
    behavior = _NS_CAN_JOIN_ALL_SPACES | _NS_STATIONARY | _NS_IGNORES_CYCLE | _NS_FULLSCREEN_AUXILIARY
    _msg_u(ns_window, "setCollectionBehavior:", behavior)
    _msg_b(ns_window, "setHidesOnDeactivate:", False)
    _msg_b(ns_window, "setCanHide:", False)
    _msg_b(ns_window, "setIgnoresMouseEvents:", True)
