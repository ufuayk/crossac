"""Community crosshair sharing.

Crosshairs are nothing but JSON blobs of :class:`CrosshairSettings`. This
module:

* pulls the community crosshair index from ``ufuayk/crossac-repo`` and
  downloads every crosshair (cached locally so offline launches still work),
* strictly validates any incoming crosshair - only known keys, typed and
  range-clamped, colours verified; nothing is ever executed,
* exports / imports crosshairs as ``.crossac.json`` files that users can
  submit back to the community repo via pull request.

The community repo is empty for now; a missing ``index.json`` simply reports
the community as "empty" instead of failing.
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from dataclasses import dataclass
from typing import List, Optional

from PySide6.QtCore import QStandardPaths, QThread, Signal

from .config import ARMS_LETTERS, CAPS, CROSSHAIR_KEYS, CrosshairSettings
from .renderer import STYLES

COMMUNITY_OWNER = "ufuayk"
COMMUNITY_REPO = "crossac-repo"

RAW_BASE = f"https://raw.githubusercontent.com/{COMMUNITY_OWNER}/{COMMUNITY_REPO}/main"
INDEX_URL = f"{RAW_BASE}/index.json"

FORMAT = "crossac"
FORMAT_VERSION = 1

_RE_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")

_INT_LIMITS = {
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
}


@dataclass
class CommunityCrosshair:
    id: str
    name: str
    author: str
    settings: CrosshairSettings


# ------------------------------------------------------------------ validate
def validate_crosshair(data: dict) -> Optional[CrosshairSettings]:
    """Turn a parsed JSON object into settings, or None if it is invalid."""
    if not isinstance(data, dict):
        return None
    settings = data.get("settings")
    if not isinstance(settings, dict):
        return None
    try:
        out = CrosshairSettings()
        for key in CROSSHAIR_KEYS:
            if key not in settings:
                continue
            value = settings[key]
            if key in ("outline", "center_dot"):
                out.__dict__[key] = bool(value)
            elif key in ("color", "outline_color", "dot_color"):
                if isinstance(value, str) and _RE_COLOR.match(value):
                    out.__dict__[key] = value.upper()
                else:
                    return None
            elif key == "style":
                if value in STYLES:
                    out.__dict__[key] = value
                else:
                    return None
            elif key == "arms":
                if isinstance(value, str) and value and set(value) <= set(ARMS_LETTERS):
                    out.__dict__[key] = "".join(letter for letter in ARMS_LETTERS if letter in value)
                else:
                    return None
            elif key == "cap":
                if value in CAPS:
                    out.__dict__[key] = value
                else:
                    return None
            else:
                try:
                    out.__dict__[key] = int(value)
                except (TypeError, ValueError):
                    return None
                low, high = _INT_LIMITS.get(key, (0, 10 ** 6))
                out.__dict__[key] = max(low, min(high, out.__dict__[key]))
        return out
    except Exception:
        return None


def _sanitize_name(value: object, fallback: str, limit: int = 60) -> str:
    if not isinstance(value, str):
        return fallback
    value = value.strip()
    if not value:
        return fallback
    return value[:limit]


# ------------------------------------------------------------- export/import
def serialize_settings(settings: CrosshairSettings, name: str, author: str = "") -> dict:
    payload = {key: getattr(settings, key) for key in CROSSHAIR_KEYS}
    return {
        "format": FORMAT,
        "version": FORMAT_VERSION,
        "name": name,
        "author": author,
        "settings": payload,
    }


def export_settings(settings: CrosshairSettings, path: str, name: str, author: str = "") -> bool:
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(serialize_settings(settings, name, author), fh, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False


def import_file(path: str) -> Optional[tuple]:
    """Load a crosshair file. Returns ``(name, author, settings)`` or None."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    settings = validate_crosshair(data)
    if settings is None:
        return None
    name = _sanitize_name(data.get("name"), "Imported crosshair")
    author = _sanitize_name(data.get("author"), "", 40)
    return name, author, settings


# -------------------------------------------------------------- fetching
def _http_get(url: str, timeout: float = 8.0) -> Optional[bytes]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "crossac/2.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except Exception:
        return None


def _download_json(url: str) -> Optional[dict]:
    raw = _http_get(url)
    if raw is None:
        return None
    try:
        data = json.loads(raw.decode("utf-8"))
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def cache_dir() -> str:
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    directory = os.path.join(base, "community")
    os.makedirs(directory, exist_ok=True)
    return directory


def _cached_path(crosshair_id: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in crosshair_id)
    return os.path.join(cache_dir(), f"{safe}.json")


def load_cached() -> List[CommunityCrosshair]:
    items = []
    directory = cache_dir()
    if not os.path.isdir(directory):
        return items
    for filename in sorted(os.listdir(directory)):
        if not filename.lower().endswith(".json"):
            continue
        result = import_file(os.path.join(directory, filename))
        if result is None:
            continue
        name, author, settings = result
        items.append(CommunityCrosshair(filename[:-5], name, author, settings))
    return items


def _fetch_all() -> tuple:
    """Fetch the community index + crosshairs. Returns ``(items, status, message)``."""
    index = _download_json(INDEX_URL)
    if index is None:
        # offline or not created yet - fall back to local cache
        cached = load_cached()
        if cached:
            return cached, "cached", "offline"
        return [], "empty", "index_missing"

    entries = index.get("crosshairs", [])
    if not isinstance(entries, list) or not entries:
        return [], "empty", "no_crosshairs"

    items: List[CommunityCrosshair] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        crosshair_id = _sanitize_name(entry.get("id"), "", 40)
        if not crosshair_id:
            continue
        file_path = _sanitize_name(entry.get("file"), "", 120)
        if not file_path:
            continue
        url = f"{RAW_BASE}/{file_path}"
        data = _download_json(url)
        settings = validate_crosshair(data) if data else None
        if settings is None:
            continue
        name = _sanitize_name(entry.get("name") or (data or {}).get("name"), crosshair_id)
        author = _sanitize_name(entry.get("author") or (data or {}).get("author"), "", 40)
        items.append(CommunityCrosshair(crosshair_id, name, author, settings))
        try:
            with open(_cached_path(crosshair_id), "w", encoding="utf-8") as fh:
                json.dump(serialize_settings(settings, name, author), fh, ensure_ascii=False)
        except OSError:
            pass
    return items, "ok", ""


class CommunityWorker(QThread):
    """Fetch the community library without blocking the UI thread."""

    done = Signal(object)

    def run(self) -> None:
        items, status, message = _fetch_all()
        self.done.emit({"items": items, "status": status, "message": message})
