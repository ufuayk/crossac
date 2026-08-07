"""Lightweight, dependency-free translation system.

Translations live as simple JSON files in the ``translations/`` folder
(next to ``main.py``). Adding a new language is as easy as dropping a new
``xx.json`` file in there; the language will automatically appear in the
language selector.

Each file uses the following schema::

    {
        "locale": "tr",        # ISO language code, used for persisting the choice
        "name": "Türkçe",      # native name shown in the language dropdown
        "translations": {
            "settings": "Ayarlar",
            ...
        }
    }

The missing keys fall back to English automatically, so partial translations
are fine. In the UI code call ``tr("key")`` instead of hard-coded strings.
"""

from __future__ import annotations

import json
import locale
import os
from typing import Dict, List, Optional

TRANSLATIONS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "translations"
)
TRANSLATIONS_DIR = os.path.normpath(TRANSLATIONS_DIR)


class I18n:
    """Loads and looks up translations for a single locale."""

    def __init__(self, directory: str = TRANSLATIONS_DIR):
        self.directory = directory
        self.current_locale: str = "en"
        self._tables: Dict[str, Dict[str, str]] = {}
        self._load_default("en")
        self.discover()

    # ------------------------------------------------------------------ loaders
    def _load_file(self, path: str) -> Optional[Dict[str, str]]:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data.get("translations", {})
        except (OSError, ValueError, AttributeError):
            return None

    def _load_default(self, locale_code: str) -> None:
        """English is the embedded fallback so the app works with zero files."""
        if locale_code != "en":
            return
        self._tables.setdefault("en", {})

    def discover(self) -> None:
        """Scan the translations folder and load every available locale."""
        self._tables.setdefault("en", {})
        if not os.path.isdir(self.directory):
            return
        for filename in sorted(os.listdir(self.directory)):
            if not filename.lower().endswith(".json"):
                continue
            path = os.path.join(self.directory, filename)
            table = self._load_file(path)
            if table is None:
                continue
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                locale_code = data.get("locale", filename[:-5])
            except (OSError, ValueError):
                locale_code = filename[:-5]
            self._tables[locale_code] = dict(self._tables.get(locale_code, {}))
            self._tables[locale_code].update(table)

    # ------------------------------------------------------------------- lookup
    def available_locales(self) -> List[str]:
        return sorted(self._tables.keys())

    def locale_name(self, locale_code: str) -> str:
        path = os.path.join(self.directory, f"{locale_code}.json")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh).get("name", locale_code)
        except (OSError, ValueError):
            return locale_code

    def set_locale(self, locale_code: str) -> bool:
        if locale_code not in self._tables:
            return False
        self.current_locale = locale_code
        return True

    def system_locale(self) -> str:
        try:
            code, _ = locale.getdefaultlocale()
            if code:
                return code.split("_")[0].lower()
        except Exception:
            pass
        try:
            for env in ("LANG", "LC_ALL", "LC_MESSAGES"):
                if env in os.environ and os.environ[env]:
                    return os.environ[env].split(".")[0].split("_")[0].lower()
        except Exception:
            pass
        return "en"

    def tr(self, key: str) -> str:
        table = self._tables.get(self.current_locale)
        if table and key in table:
            return table[key]
        fallback = self._tables.get("en", {})
        return fallback.get(key, key)


_i18n: Optional[I18n] = None


def init_i18n(locale_code: Optional[str] = None) -> I18n:
    global _i18n
    _i18n = I18n()
    if locale_code and _i18n.set_locale(locale_code):
        return _i18n
    sys_locale = _i18n.system_locale()
    if _i18n.set_locale(sys_locale):
        return _i18n
    _i18n.set_locale("en")
    return _i18n


def get_i18n() -> I18n:
    assert _i18n is not None, "init_i18n() must be called before get_i18n()"
    return _i18n


def tr(key: str) -> str:
    """Translate a key using the active locale (falls back to English)."""
    return get_i18n().tr(key)
