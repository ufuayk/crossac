from __future__ import annotations

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QToolButton,
    QVBoxLayout,
)

from .i18n import tr

QUICK_COLORS = (
    "#FFFFFF", "#D6DAE2", "#8B94A6", "#000000",
    "#00FF88", "#2FF3B2", "#00B4FF", "#4C6FFF",
    "#7C4DFF", "#FF4D6D", "#FF6D00", "#FFD500",
    "#FF1744", "#00C853", "#FF7EB3", "#FF9800",
)


def _valid_hex(text: str) -> bool:
    text = text.strip().lstrip("#")
    if len(text) != 6:
        return False
    try:
        int(text, 16)
        return True
    except ValueError:
        return False


class ColorPopup(QFrame):
    def __init__(self, store, key: str, parent):
        super().__init__(parent)
        self._store = store
        self._key = key
        self.setObjectName("colorPopup")
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(8)

        self._title = QLabel(tr("color.palette"))
        self._title.setObjectName("popupTitle")
        root.addWidget(self._title)

        grid = QGridLayout()
        grid.setSpacing(6)
        for i, color in enumerate(QUICK_COLORS):
            btn = QToolButton()
            btn.setObjectName("swatchButton")
            btn.setFixedSize(26, 26)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(color)
            btn.setStyleSheet(f"background-color: {color};")
            btn.clicked.connect(lambda checked=False, c=color: self._apply(c))
            grid.addWidget(btn, i // 8, i % 8)
        root.addLayout(grid)

        bottom = QHBoxLayout()
        bottom.setSpacing(6)
        self._hex = QLineEdit()
        self._hex.setPlaceholderText(tr("color.hex_tip"))
        self._hex.setMaxLength(7)
        self._hex.setClearButtonEnabled(True)
        self._hex.returnPressed.connect(self._apply_hex)
        self._hex.textChanged.connect(self._on_hex_changed)
        self._custom_btn = QPushButton(tr("color.custom"))
        self._custom_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._custom_btn.clicked.connect(self._custom_dialog)
        bottom.addWidget(self._hex, 1)
        bottom.addWidget(self._custom_btn)
        root.addLayout(bottom)

        self._store.changed.connect(self._sync_hex)
        self._sync_hex()

    def _apply(self, color: str) -> None:
        self._store.set(**{self._key: color})

    def _apply_hex(self) -> None:
        text = self._hex.text().strip()
        if text and not text.startswith("#"):
            text = f"#{text}"
        if _valid_hex(text):
            self._apply(text.upper())
            self.hide()

    def _on_hex_changed(self, text: str) -> None:
        if _valid_hex(text):
            self._store.set(**{self._key: text.upper()})

    def _custom_dialog(self) -> None:
        current = QColor(getattr(self._store.get(), self._key))
        color = QColorDialog.getColor(current, self, tr("setting.color"))
        if color.isValid():
            self._store.set(**{self._key: color.name().upper()})

    def _sync_hex(self) -> None:
        value = getattr(self._store.get(), self._key)
        self._hex.blockSignals(True)
        self._hex.setText(value)
        self._hex.blockSignals(False)

    def retranslate(self) -> None:
        self._title.setText(tr("color.palette"))
        self._hex.setPlaceholderText(tr("color.hex_tip"))
        self._custom_btn.setText(tr("color.custom"))
        self._sync_hex()


class ColorButton(QToolButton):
    def __init__(self, store, key: str, parent=None):
        super().__init__(parent)
        self._store = store
        self._key = key
        self._popup: ColorPopup | None = None
        self.setObjectName("colorButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._open_popup)
        self._store.changed.connect(self._refresh)
        self._refresh()

    def _refresh(self) -> None:
        color = getattr(self._store.get(), self._key)
        self.setStyleSheet(
            f"background-color: {color}; "
            f"border: 1px solid rgba(255,255,255,0.18); "
            f"border-radius: 7px;"
        )
        self.setToolTip(color)

    def _open_popup(self) -> None:
        if self._popup is None:
            self._popup = ColorPopup(self._store, self._key, self)
        self._popup.retranslate()
        pos = self.mapToGlobal(QPoint(0, self.height() + 6))
        self._popup.move(pos)
        self._popup.show()

    def retranslate(self) -> None:
        if self._popup is not None:
            self._popup.retranslate()
