"""Persistent, cross-platform application settings built on QSettings.

The ``CrosshairSettings`` dataclass holds every option the user can tweak.
Changes are written to the platform-native settings store (Windows registry,
macOS ``defaults`` / plist, Linux ``~/.config``) the moment they are applied,
so the crosshair configuration survives restarts.

A crosshair is defined purely by numbers and colours - this is what makes the
community sharing format possible (see ``community.py``): any crosshair is a
plain JSON blob of these fields.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

from PySide6.QtCore import QSettings, Signal, QObject

ORG = "Crossac"
APP = "Crossac"

# machine-readable keys that fully describe a crosshair (used for export/import)
CROSSHAIR_KEYS = (
    "style",
    "sides",      # polygon corner count for the circle style (3..64)
    "size",       # horizontal line length  (px)
    "size_v",     # vertical line length    (px)
    "gap",        # horizontal inner gap    (px)
    "gap_v",      # vertical inner gap      (px)
    "arms",       # which arms the cross draws: letters from "tlbr"
    "thickness",  # stroke width            (px)
    "cap",        # line cap: flat | round | square
    "color",
    "opacity",    # 10..100 %
    "rotation",   # degrees
    "outline",
    "outline_color",
    "outline_thickness",
    "center_dot",
    "dot_size",
    "dot_color",
    "offset_x",   # pixel nudge from dead center
    "offset_y",
)

NON_CROSSHAIR_KEYS = ("monitor", "language")

BUILTIN_STYLES = ("cross", "circle", "dot")
ARMS_LETTERS = ("t", "b", "l", "r")
CAPS = ("flat", "round", "square")


@dataclass
class CrosshairSettings:
    style: str = "cross"                 # cross | circle | dot
    sides: int = 64                      # polygon corners for "circle" (>=3 = polygon)
    size: int = 26
    size_v: int = 26
    gap: int = 6
    gap_v: int = 6
    arms: str = "tlbr"                   # subset of "tlbr": top,bottom,left,right
    thickness: int = 3
    cap: str = "flat"                    # flat | round | square
    color: str = "#00FF00"
    opacity: int = 100
    rotation: int = 0

    outline: bool = False
    outline_color: str = "#000000"
    outline_thickness: int = 2

    center_dot: bool = True
    dot_size: int = 3
    dot_color: str = "#00FF00"

    offset_x: int = 0
    offset_y: int = 0

    monitor: int = 0
    language: str = ""                   # empty == system language


DEFAULTS = CrosshairSettings()


class SettingsStore(QObject):
    """Bridges :class:`CrosshairSettings` and QSettings + change signals."""

    changed = Signal()

    def __init__(self):
        super().__init__()
        self._settings = CrosshairSettings()
        self._q = QSettings(ORG, APP)
        self.load()

    # ------------------------------------------------------------- load/save
    def load(self) -> None:
        q = self._q
        s = self._settings
        for key in CROSSHAIR_KEYS + NON_CROSSHAIR_KEYS:
            if q.contains(key):
                setattr(s, key, q.value(key))
        # sanitise values that may have come from older versions / config files
        if s.style not in BUILTIN_STYLES:
            s.style = "cross"
        if not isinstance(s.sides, int) or not (3 <= s.sides <= 64):
            s.sides = 64
        if not isinstance(s.arms, str) or not set(s.arms) or not set(s.arms) <= set(ARMS_LETTERS):
            s.arms = "tlbr"
        if not isinstance(s.cap, str) or s.cap not in CAPS:
            s.cap = "flat"

    def save(self) -> None:
        q = self._q
        for key, value in asdict(self._settings).items():
            q.setValue(key, value)
        q.sync()

    def reset(self) -> None:
        self._settings = CrosshairSettings()
        for key in CROSSHAIR_KEYS + NON_CROSSHAIR_KEYS:
            self._q.remove(key)
        self._q.sync()
        self.changed.emit()

    # ------------------------------------------------------------------ get
    @property
    def data(self) -> CrosshairSettings:
        return self._settings

    def get(self) -> CrosshairSettings:
        return self._settings

    # ------------------------------------------------------------------ set
    def set(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)
        self.save()
        self.changed.emit()

    def apply(self, settings: CrosshairSettings) -> None:
        self._settings = settings
        self.save()
        self.changed.emit()
