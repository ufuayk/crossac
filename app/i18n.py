from __future__ import annotations

import json
import locale
import os
import re
import subprocess
import sys
from typing import Dict, List, Optional

TRANSLATIONS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "translations")
)


class I18n:
    def __init__(self, directory: str = TRANSLATIONS_DIR):
        self.directory = directory
        self.current_locale: str = "en"
        self._tables: Dict[str, Dict[str, str]] = {}
        self._names: Dict[str, str] = {}
        self.discover()

    def discover(self) -> None:
        self._tables = {"en": {}}
        self._names = {"en": "English"}
        if not os.path.isdir(self.directory):
            return
        for filename in sorted(os.listdir(self.directory)):
            if not filename.lower().endswith(".json"):
                continue
            path = os.path.join(self.directory, filename)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except (OSError, ValueError):
                continue
            if not isinstance(data, dict):
                continue
            table = data.get("translations")
            if not isinstance(table, dict):
                continue
            locale_code = data.get("locale") or filename[:-5]
            self._tables[locale_code] = dict(self._tables.get(locale_code, {}))
            self._tables[locale_code].update(table)
            name = data.get("name")
            if isinstance(name, str) and name:
                self._names[locale_code] = name

    def available_locales(self) -> List[str]:
        return sorted(self._tables.keys())

    def locale_name(self, locale_code: str) -> str:
        return self._names.get(locale_code, locale_code)

    def set_locale(self, locale_code: str) -> bool:
        if locale_code not in self._tables:
            return False
        self.current_locale = locale_code
        return True

    def system_locale(self) -> str:
        if sys.platform == "darwin":
            code = self._system_from_macos()
            if code:
                return code
        code = self._system_from_env()
        if code:
            return code
        code = self._system_from_locale()
        if code:
            return code
        return "en"

    @staticmethod
    def _system_from_macos() -> Optional[str]:
        try:
            result = subprocess.run(
                ["defaults", "read", "NSGlobalDomain", "AppleLanguages"],
                capture_output=True, text=True, timeout=2,
            )
            match = re.search(r'"([a-zA-Z]{2,3})(?:[-_][a-zA-Z]{2,4})?"', result.stdout or "")
            if match:
                return match.group(1).lower()
        except Exception:
            pass
        return None

    @staticmethod
    def _system_from_env() -> Optional[str]:
        for env in ("LC_ALL", "LC_MESSAGES", "LANG"):
            value = os.environ.get(env, "")
            if value:
                return value.split(".")[0].split("_")[0].lower()
        return None

    @staticmethod
    def _system_from_locale() -> Optional[str]:
        try:
            code, _ = locale.getdefaultlocale()
            if code:
                return code.split("_")[0].lower()
        except Exception:
            pass
        return None

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
    _i18n.set_locale(_i18n.system_locale())
    return _i18n


def get_i18n() -> I18n:
    assert _i18n is not None, "init_i18n() must be called before get_i18n()"
    return _i18n


def tr(key: str) -> str:
    return get_i18n().tr(key)
