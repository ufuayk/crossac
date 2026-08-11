from __future__ import annotations

import json
import os
import re
import urllib.request
from dataclasses import dataclass
from typing import List, Optional

from PySide6.QtCore import QStandardPaths, QThread, Signal

from .config import ARMS_LETTERS, CAPS, CROSSHAIR_KEYS, INT_LIMITS, CrosshairSettings
from .renderer import STYLES

COMMUNITY_OWNER = "ufuayk"
COMMUNITY_REPO = "crossac-repo"

RAW_BASE = f"https://raw.githubusercontent.com/{COMMUNITY_OWNER}/{COMMUNITY_REPO}/main"
INDEX_URL = f"{RAW_BASE}/index.json"

FORMAT = "crossac"
FORMAT_VERSION = 1

_HTTP_TIMEOUT = 5.0
_RE_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


@dataclass
class CommunityCrosshair:
    id: str
    name: str
    author: str
    settings: CrosshairSettings


def _as_bool(value, default=False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return default


def validate_crosshair(data: dict) -> Optional[CrosshairSettings]:
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
                out.__dict__[key] = _as_bool(value)
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
                    ivalue = int(value)
                except (TypeError, ValueError):
                    return None
                low, high = INT_LIMITS.get(key, (0, 10 ** 6))
                out.__dict__[key] = max(low, min(high, ivalue))
        return out
    except Exception:
        return None


def _sanitize_name(value, fallback: str, limit: int = 60) -> str:
    if not isinstance(value, str):
        return fallback
    value = value.strip()
    if not value:
        return fallback
    return value[:limit]


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


def _http_get(url: str, timeout: float = _HTTP_TIMEOUT) -> Optional[bytes]:
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


def _fetch_all(should_stop=None) -> tuple:
    index = _download_json(INDEX_URL)
    if should_stop and should_stop():
        return [], "cancelled", ""
    if index is None:
        cached = load_cached()
        if cached:
            return cached, "cached", "offline"
        return [], "empty", "index_missing"

    entries = index.get("crosshairs", [])
    if not isinstance(entries, list) or not entries:
        return [], "empty", "no_crosshairs"

    items: List[CommunityCrosshair] = []
    for entry in entries:
        if should_stop and should_stop():
            return [], "cancelled", ""
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
        if should_stop and should_stop():
            return [], "cancelled", ""
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
    done = Signal(object)

    def run(self) -> None:
        items, status, message = _fetch_all(should_stop=self.isInterruptionRequested)
        if not self.isInterruptionRequested():
            self.done.emit({"items": items, "status": status, "message": message})
