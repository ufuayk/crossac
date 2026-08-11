from __future__ import annotations

import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QWidget

from .config import SettingsStore
from .native import apply_topmost
from .renderer import logical_size, render_pixmap


class OverlayWindow(QWidget):
    def __init__(self, store: SettingsStore):
        super().__init__()
        self._store = store
        self._pixmap: QPixmap = QPixmap()
        self._native_timer = QTimer(self)
        self._native_timer.setInterval(1500)
        self._native_timer.timeout.connect(self._apply_native)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self._store.changed.connect(self.refresh)
        self.refresh()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_native()
        if sys.platform == "darwin":
            self._native_timer.start()
        else:
            self._native_timer.stop()

    def hideEvent(self, event) -> None:
        self._native_timer.stop()
        super().hideEvent(event)

    def closeEvent(self, event) -> None:
        self._native_timer.stop()
        super().closeEvent(event)

    def _apply_native(self) -> None:
        if self.isVisible() and self.windowHandle() is not None:
            apply_topmost(self)

    def refresh(self) -> None:
        settings = self._store.get()
        screen = self._target_screen()
        dpr = screen.devicePixelRatio() if screen else QApplication.primaryScreen().devicePixelRatio()

        self._pixmap = render_pixmap(settings, dpr)
        width, height = logical_size(settings, dpr)
        self.resize(int(width), int(height))
        self.center_on(screen)
        self.update()

    def _target_screen(self):
        screens = QApplication.screens()
        if not screens:
            return None
        index = self._store.get().monitor
        if 0 <= index < len(screens):
            return screens[index]
        return QApplication.primaryScreen()

    def center_on(self, screen) -> None:
        if screen is None:
            return
        settings = self._store.get()
        geometry = screen.geometry()
        x = geometry.x() + (geometry.width() - self.width()) // 2 + settings.offset_x
        y = geometry.y() + (geometry.height() - self.height()) // 2 + settings.offset_y
        self.move(x, y)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, self._pixmap)
        painter.end()

    def toggle(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show()
