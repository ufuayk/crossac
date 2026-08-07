"""System tray integration built on Qt's own QSystemTrayIcon.

Using Qt's native tray support keeps the app dependency-free and identical on
Windows, macOS and Linux (pystray is no longer needed).
"""

from __future__ import annotations

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from .config import SettingsStore
from .i18n import tr
from .renderer import render_icon


class TrayIcon:
    def __init__(self, store: SettingsStore, overlay, dialog):
        self._store = store
        self._overlay = overlay
        self._dialog = dialog

        self._menu = QMenu()
        self._settings_action = QAction(tr("tray.settings"), self._menu)
        self._settings_action.triggered.connect(self._open_settings)
        self._quit_action = QAction(tr("tray.quit"), self._menu)
        self._quit_action.triggered.connect(self._quit)

        self._menu.addAction(self._settings_action)
        self._menu.addSeparator()
        self._menu.addAction(self._quit_action)

        self._icon = QSystemTrayIcon(self._icon_pixmap(), None)
        self._icon.setContextMenu(self._menu)
        self._icon.setToolTip(tr("tray.tooltip"))
        self._icon.activated.connect(self._on_activated)
        self._store.changed.connect(self._refresh_icon)
        self._icon.show()

    def _icon_pixmap(self):
        return render_icon(self._store.get(), 64)

    def _refresh_icon(self) -> None:
        self._icon.setIcon(self._icon_pixmap())

    def _open_settings(self) -> None:
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()

    def _on_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._open_settings()

    def _quit(self) -> None:
        self._icon.hide()
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
