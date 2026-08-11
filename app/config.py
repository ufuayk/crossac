from __future__ import annotations

import re
from dataclasses import dataclass, asdict

from PySide6.QtCore import QSettings, Signal, QObject

ORG = "Crossac"
APP = "Crossac"

CROSSHAIR_KEYS = (
    "style",
    "sides",
    "size",
    "size_v",
    "gap",
    "gap_v",
    "arms",
    "thickness",
    "cap",
    "color",
    "opacity",
    "rotation",
    "outline",
    "outline_color",
    "outline_thickness",
    "center_dot",
    "dot_size",
    "dot_color",
    "offset_x",
    "offset_y",
)

NON_CROSSHAIR_KEYS = ("monitor", "language")

BUILTIN_STYLES = ("cross", "circle", "dot")
ARMS_LETTERS = ("t", "b", "l", "r")
CAPS = ("flat", "round", "square")

INT_LIMITS = {
    "sides": (3, 64),
    "size": (2, 200),
    "size_v": (2, 200),
    "gap": (0, 100),
    "gap_v": (0, 100),
    "thickness": (1, 40),
    "opacity": (10, 100),
    "rotation": (0, 360),
    "outline_thickness": (1, 20),
    "dot_size": (1, 80),
    "offset_x": (-400, 400),
    "offset_y": (-400, 400),
    "monitor": (0, 100),
}

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _as_bool(value, default=False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return default


def _as_int(value, low: int, high: int, default: int) -> int:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        ivalue = default
    return max(low, min(high, ivalue))


def _as_color(value, default: str) -> str:
    if isinstance(value, str) and _HEX_RE.match(value):
        return value.upper()
    return default


@dataclass
class CrosshairSettings:
    style: str = "cross"
    sides: int = 64
    size: int = 26
    size_v: int = 26
    gap: int = 6
    gap_v: int = 6
    arms: str = "tlbr"
    thickness: int = 3
    cap: str = "flat"
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
    language: str = ""


DEFAULTS = CrosshairSettings()


class SettingsStore(QObject):
    changed = Signal()

    def __init__(self):
        super().__init__()
        self._settings = CrosshairSettings()
        self._q = QSettings(ORG, APP)
        self.load()

    def load(self) -> None:
        q = self._q
        s = self._settings
        for key in CROSSHAIR_KEYS + NON_CROSSHAIR_KEYS:
            if not q.contains(key):
                continue
            value = q.value(key)
            if key in ("outline", "center_dot"):
                setattr(s, key, _as_bool(value))
            elif key in ("color", "outline_color", "dot_color"):
                setattr(s, key, _as_color(value, getattr(s, key)))
            elif key == "style":
                if value in BUILTIN_STYLES:
                    s.style = value
            elif key == "arms":
                if isinstance(value, str) and value and set(value) <= set(ARMS_LETTERS):
                    s.arms = "".join(letter for letter in ARMS_LETTERS if letter in value)
            elif key == "cap":
                if value in CAPS:
                    s.cap = value
            elif key in INT_LIMITS:
                low, high = INT_LIMITS[key]
                setattr(s, key, _as_int(value, low, high, getattr(s, key)))
            else:
                setattr(s, key, value)

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

    @property
    def data(self) -> CrosshairSettings:
        return self._settings

    def get(self) -> CrosshairSettings:
        return self._settings

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
