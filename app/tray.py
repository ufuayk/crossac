# dynamic tray icon

from __future__ import annotations

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QAction, QActionGroup, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from .colorbutton import QUICK_COLORS
from .config import SettingsStore
from .i18n import tr
from .renderer import STYLES, render_icon

_OPACITIES = (40, 60, 80, 100)


class TrayIcon:
    def __init__(self, store: SettingsStore, overlay, dialog):
        self._store = store
        self._overlay = overlay
        self._dialog = dialog
        self._last_language = store.get().language
        self._style_actions = {}
        self._opacity_actions = {}
        self._monitor_actions = {}

        self._menu = QMenu()
        self._icon = QSystemTrayIcon(self._icon_pixmap(), None)
        self._icon.setContextMenu(self._menu)
        self._icon.activated.connect(self._on_activated)
        self._store.changed.connect(self._on_store_changed)

        self._rebuild_menu()
        self._icon.show()

    def _rebuild_menu(self) -> None:
        menu = self._menu
        menu.clear()

        self._toggle_action = QAction(tr("tray.show"), menu)
        self._toggle_action.triggered.connect(self._toggle_overlay)
        menu.addAction(self._toggle_action)
        menu.addSeparator()

        style_menu = menu.addMenu(tr("tray.style"))
        self._style_actions = {}
        self._style_group = QActionGroup(menu)
        self._style_group.setExclusive(True)
        for style in STYLES:
            action = QAction(tr(f"style.{style}"), style_menu)
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked=False, s=style: self._store.set(style=s))
            self._style_group.addAction(action)
            self._style_actions[style] = action
            style_menu.addAction(action)

        color_menu = menu.addMenu(tr("tray.color"))
        self._color_actions = []
        for color in QUICK_COLORS:
            action = QAction(self._swatch(color), color.upper(), color_menu)
            action.triggered.connect(
                lambda checked=False, c=color: self._store.set(color=c))
            self._color_actions.append(action)
            color_menu.addAction(action)

        opacity_menu = menu.addMenu(tr("tray.opacity"))
        self._opacity_actions = {}
        self._opacity_group = QActionGroup(menu)
        self._opacity_group.setExclusive(True)
        for value in _OPACITIES:
            action = QAction(f"{value}%", opacity_menu)
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked=False, v=value: self._store.set(opacity=v))
            self._opacity_group.addAction(action)
            self._opacity_actions[value] = action
            opacity_menu.addAction(action)

        monitor_menu = menu.addMenu(tr("tray.monitor"))
        self._monitor_actions = {}
        self._monitor_group = QActionGroup(menu)
        self._monitor_group.setExclusive(True)
        screens = QApplication.screens()
        for index, screen in enumerate(screens):
            if index == 0:
                label = tr("monitor.primary")
            else:
                label = f"{screen.name() or f'Monitor {index + 1}'} ({index + 1})"
            action = QAction(label, monitor_menu)
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked=False, i=index: self._store.set(monitor=i))
            self._monitor_group.addAction(action)
            self._monitor_actions[index] = action
            monitor_menu.addAction(action)

        menu.addSeparator()
        self._settings_action = QAction(tr("tray.settings"), menu)
        self._settings_action.triggered.connect(self._open_settings)
        menu.addAction(self._settings_action)

        menu.addSeparator()
        self._quit_action = QAction(tr("tray.quit"), menu)
        self._quit_action.triggered.connect(self._quit)
        menu.addAction(self._quit_action)

        self._sync_menu_state()

    @staticmethod
    def _swatch(color: str, size: int = 14) -> QIcon:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(color))
        painter.drawRoundedRect(QRectF(1, 1, size - 2, size - 2), 3, 3)
        painter.end()
        return QIcon(pixmap)

    def _toggle_overlay(self) -> None:
        self._overlay.toggle()
        self._sync_menu_state()

    def _open_settings(self) -> None:
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()

    def _on_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._open_settings()

    def _quit(self) -> None:
        if self._dialog is not None:
            self._dialog.request_worker_stop()
            self._dialog.wait_for_worker(5500)
        self._icon.hide()
        from PySide6.QtWidgets import QApplication
        QApplication.quit()

    def _on_store_changed(self) -> None:
        language = self._store.get().language
        if language != self._last_language:
            self._last_language = language
            self._rebuild_menu()
        else:
            self._sync_menu_state()

    def _sync_menu_state(self) -> None:
        settings = self._store.get()
        visible = self._overlay.isVisible()
        self._toggle_action.setText(tr("tray.hide") if visible else tr("tray.show"))
        for style, action in self._style_actions.items():
            action.setChecked(style == settings.style)
        for value, action in self._opacity_actions.items():
            action.setChecked(value == settings.opacity)
        for index, action in self._monitor_actions.items():
            action.setChecked(index == settings.monitor)
        self._icon.setIcon(self._icon_pixmap())
        self._icon.setToolTip(self._tooltip(settings, visible))

    def _tooltip(self, settings, visible: bool) -> str:
        state = tr("tray.visible") if visible else tr("tray.hidden")
        style = tr(f"style.{settings.style}")
        color = getattr(settings, "color", "")
        return f"{tr('tray.tooltip')} · {style} · {color} · {state}"

    def _icon_pixmap(self) -> QPixmap:
        pixmap = render_icon(self._store.get(), 64)
        if not self._overlay.isVisible():
            dimmed = QPixmap(pixmap.size())
            dimmed.fill(Qt.transparent)
            painter = QPainter(dimmed)
            painter.setOpacity(0.3)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            return dimmed
        return pixmap
