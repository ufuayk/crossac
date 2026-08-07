"""Settings dialog with live preview, detailed customisation and the
community crosshair library.

Every control writes straight into the shared :class:`SettingsStore`, which
re-emits ``changed`` so the overlay and the preview update instantly. The whole
UI is translated on the fly when the language is changed.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QPainter
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSizePolicy,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QApplication,
)

from .community import CommunityWorker, export_settings, import_file
from .config import ARMS_LETTERS, CAPS, CrosshairSettings, SettingsStore
from .i18n import get_i18n, tr
from .renderer import STYLES, render_pixmap

# (settings key, translation key, min, max) - in display order
_APPEARANCE_SLIDERS = (
    ("size", "setting.size", 2, 200),
    ("size_v", "setting.size_v", 2, 200),
    ("gap", "setting.gap", 0, 100),
    ("gap_v", "setting.gap_v", 0, 100),
    ("thickness", "setting.thickness", 1, 40),
    ("rotation", "setting.rotation", 0, 360),
    ("opacity", "setting.opacity", 10, 100),
    ("offset_x", "setting.offset_x", -300, 300),
    ("offset_y", "setting.offset_y", -300, 300),
)

_ARMS_LABELS = (
    ("t", "setting.arm_top"),
    ("b", "setting.arm_bottom"),
    ("l", "setting.arm_left"),
    ("r", "setting.arm_right"),
)


class CrosshairPreview(QWidget):
    """Renders the crosshair scaled to fit, updating live with the settings.

    Rendered at dpr 1.0 and pre-scaled, so there is no high-DPI pixmap /
    source-rectangle confusion that could clip or ghost the preview.
    """

    def __init__(self, store: SettingsStore, parent=None):
        super().__init__(parent)
        self._store = store
        self.setObjectName("previewPanel")
        self.setMinimumSize(320, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._pixmap = render_pixmap(store.get(), 1.0)
        self._store.changed.connect(self._on_changed)

    def _on_changed(self) -> None:
        self._pixmap = render_pixmap(self._store.get(), 1.0)
        self.update()

    def paintEvent(self, event) -> None:
        if self._pixmap.isNull():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        scale = min(
            self.width() / self._pixmap.width(),
            self.height() / self._pixmap.height(),
            1.8,
        )
        w = max(int(self._pixmap.width() * scale), 1)
        h = max(int(self._pixmap.height() * scale), 1)
        scaled = self._pixmap.scaled(
            w, h, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        painter.end()


class SettingsDialog(QDialog):
    def __init__(self, store: SettingsStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._worker = None
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(720, 820)
        self.setMinimumSize(600, 700)
        self.setSizeGripEnabled(True)

        self._style_buttons = []
        self._sliders = {}
        self._color_buttons = {}
        self._value_labels = {}
        self._control_labels = {}
        self._arm_checks = {}

        self._build_ui()
        self._retranslate()
        self._sync_controls()
        self._update_shape_specific()
        self._store.changed.connect(self._on_store_changed)
        self._start_community_fetch()

    def _on_store_changed(self) -> None:
        self._sync_controls()
        self._update_shape_specific()

    # ------------------------------------------------------------------- UI
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 12)
        root.setSpacing(10)

        self._title = QLabel("Crossac")
        self._title.setStyleSheet("font-size: 20px; font-weight: 800; letter-spacing: 1px; color: #00ff88;")
        self._subtitle = QLabel()
        self._subtitle.setObjectName("hintLabel")
        root.addWidget(self._title)
        root.addWidget(self._subtitle)

        tabs = QTabWidget()
        tabs.addTab(self._build_crosshair_tab(), "")
        tabs.addTab(self._build_community_tab(), "")
        root.addWidget(tabs, 1)

        self._hint = QLabel()
        self._hint.setObjectName("hintLabel")
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._hint)

        buttons = QHBoxLayout()
        self._export_btn = QPushButton()
        self._export_btn.clicked.connect(self._on_export)
        self._reset_btn = QPushButton()
        self._reset_btn.setObjectName("dangerButton")
        self._reset_btn.clicked.connect(self._on_reset)
        self._close_btn = QPushButton()
        self._close_btn.setObjectName("primaryButton")
        self._close_btn.clicked.connect(self.accept)
        buttons.addWidget(self._export_btn)
        buttons.addWidget(self._reset_btn)
        buttons.addStretch(1)
        buttons.addWidget(self._close_btn)
        root.addLayout(buttons)

    def _build_crosshair_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        layout.addWidget(self._build_style_row())
        self._preview = CrosshairPreview(self._store)
        layout.addWidget(self._preview, 1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 6, 0)
        body_layout.setSpacing(10)
        body_layout.addWidget(self._build_appearance_box())
        self._arms_box = self._build_arms_box()
        body_layout.addWidget(self._arms_box)
        self._sides_box = self._build_sides_box()
        body_layout.addWidget(self._sides_box)
        body_layout.addWidget(self._build_reticle_box())
        body_layout.addWidget(self._build_outline_box())
        body_layout.addWidget(self._build_display_box())
        body_layout.addStretch(1)
        scroll.setWidget(body)
        layout.addWidget(scroll, 3)
        return tab

    def _build_style_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self._style_group = QButtonGroup(self)
        self._style_group.setExclusive(True)
        for style in STYLES:
            btn = QToolButton()
            btn.setObjectName("styleButton")
            btn.setCheckable(True)
            btn.setIcon(self._style_icon(style))
            btn.setIconSize(QSize(38, 38))
            btn.setMinimumSize(72, 54)
            btn.clicked.connect(lambda checked=False, s=style: self._store.set(style=s))
            self._style_group.addButton(btn)
            self._style_buttons.append(btn)
            layout.addWidget(btn)
        layout.addStretch(1)
        return row

    def _style_icon(self, style: str) -> QIcon:
        s = CrosshairSettings(style=style, size=14, thickness=3, gap=4,
                              color="#00ff88", center_dot=False, sides=16)
        pixmap = render_pixmap(s, 1.0)
        scaled = pixmap.scaled(44, 44, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        return QIcon(scaled)

    # ------------------------------------------------------------- boxes
    def _build_appearance_box(self) -> QGroupBox:
        box = QGroupBox()
        grid = QGridLayout(box)
        grid.setSpacing(8)
        row = 0
        for key, _, low, high in _APPEARANCE_SLIDERS:
            self._add_slider(grid, row, key, low, high)
            row += 1
        self._add_color(grid, row, "color")
        row += 1
        self._add_cap(grid, row)
        self._appearance_box = box
        return box

    def _build_arms_box(self) -> QGroupBox:
        box = QGroupBox()
        layout = QHBoxLayout(box)
        layout.setSpacing(8)
        self._arm_checks = {}
        for letter, _ in _ARMS_LABELS:
            check = QCheckBox()
            check.clicked.connect(self._on_arm_toggled)
            layout.addWidget(check)
            self._arm_checks[letter] = check
        layout.addStretch(1)
        return box

    def _on_arm_toggled(self) -> None:
        arms = "".join(letter for letter, _ in _ARMS_LABELS if self._arm_checks[letter].isChecked())
        self._store.set(arms=arms)

    def _build_sides_box(self) -> QGroupBox:
        box = QGroupBox()
        grid = QGridLayout(box)
        grid.setSpacing(8)
        self._add_slider(grid, 0, "sides", 3, 64)
        return box

    def _build_reticle_box(self) -> QGroupBox:
        box = QGroupBox()
        grid = QGridLayout(box)
        grid.setSpacing(8)
        self._dot_check = QCheckBox()
        self._dot_check.toggled.connect(lambda v: self._store.set(center_dot=v))
        grid.addWidget(self._dot_check, 0, 0, 1, 2)
        self._dot_color_btn = QPushButton()
        self._dot_color_btn.setObjectName("colorButton")
        self._dot_color_btn.setMaximumWidth(70)
        self._dot_color_btn.clicked.connect(self._pick_dot_color)
        grid.addWidget(self._dot_color_btn, 0, 2)
        self._add_slider(grid, 1, "dot_size", 1, 80)
        self._reticle_box = box
        return box

    def _build_outline_box(self) -> QGroupBox:
        box = QGroupBox()
        grid = QGridLayout(box)
        grid.setSpacing(8)
        self._outline_check = QCheckBox()
        self._outline_check.toggled.connect(lambda v: self._store.set(outline=v))
        grid.addWidget(self._outline_check, 0, 0, 1, 2)
        self._outline_color_btn = QPushButton()
        self._outline_color_btn.setObjectName("colorButton")
        self._outline_color_btn.setMaximumWidth(70)
        self._outline_color_btn.clicked.connect(self._pick_outline_color)
        grid.addWidget(self._outline_color_btn, 0, 2)
        self._add_slider(grid, 1, "outline_thickness", 1, 20)
        self._outline_box = box
        return box

    def _build_display_box(self) -> QGroupBox:
        box = QGroupBox()
        grid = QGridLayout(box)
        grid.setSpacing(8)
        self._monitor_label = QLabel()
        self._monitor_combo = QComboBox()
        self._populate_monitors()
        self._monitor_combo.currentIndexChanged.connect(self._on_monitor_changed)
        grid.addWidget(self._monitor_label, 0, 0, 1, 2)
        grid.addWidget(self._monitor_combo, 0, 2)

        self._language_label = QLabel()
        self._language_combo = QComboBox()
        self._rebuild_language_combo()
        self._language_combo.currentIndexChanged.connect(self._on_language_changed)
        grid.addWidget(self._language_label, 1, 0, 1, 2)
        grid.addWidget(self._language_combo, 1, 2)
        self._display_box = box
        return box

    def _update_shape_specific(self) -> None:
        style = self._store.get().style
        self._arms_box.setVisible(style == "cross")
        self._sides_box.setVisible(style == "circle")

    # ----------------------------------------------------------- community
    def _build_community_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        top = QHBoxLayout()
        self._community_status = QLabel()
        self._community_status.setObjectName("hintLabel")
        self._refresh_btn = QPushButton()
        self._refresh_btn.clicked.connect(self._start_community_fetch)
        self._import_btn = QPushButton()
        self._import_btn.clicked.connect(self._on_import)
        top.addWidget(self._community_status, 1)
        top.addWidget(self._import_btn)
        top.addWidget(self._refresh_btn)
        layout.addLayout(top)

        self._community_list = QListWidget()
        self._community_list.setIconSize(QSize(48, 48))
        self._community_list.itemClicked.connect(self._on_community_clicked)
        self._community_list.itemDoubleClicked.connect(self._on_community_clicked)
        layout.addWidget(self._community_list, 1)

        self._community_note = QLabel()
        self._community_note.setObjectName("hintLabel")
        self._community_note.setWordWrap(True)
        layout.addWidget(self._community_note)
        return tab

    def _start_community_fetch(self) -> None:
        if self._worker is not None:
            return
        self._refresh_btn.setEnabled(False)
        self._set_community_status(tr("community.loading"))
        self._community_list.clear()
        worker = CommunityWorker()
        worker.done.connect(self._on_community_done)
        worker.finished.connect(self._on_worker_finished)
        self._worker = worker
        worker.start()

    def _on_worker_finished(self) -> None:
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None

    def closeEvent(self, event) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.wait(5000)
            self._worker = None
        super().closeEvent(event)

    def _on_community_done(self, result: dict) -> None:
        self._refresh_btn.setEnabled(True)
        items = result.get("items", [])
        if not items:
            self._set_community_status(tr("community.empty"))
            self._set_community_note(tr("community.empty_note"))
            return
        self._set_community_status(tr("community.count").format(count=len(items)))
        self._set_community_note(tr("community.note"))
        for item in items:
            preview = render_pixmap(item.settings, 1.0).scaled(
                48, 48, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            list_item = QListWidgetItem(QIcon(preview), f"{item.name}\n{item.author}")
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self._community_list.addItem(list_item)

    def _set_community_status(self, text: str) -> None:
        self._community_status.setText(text)

    def _set_community_note(self, text: str) -> None:
        self._community_note.setText(text)

    def _on_community_clicked(self, item: QListWidgetItem) -> None:
        community_item = item.data(Qt.ItemDataRole.UserRole)
        if community_item is not None:
            self._store.apply(community_item.settings)

    def _on_import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, tr("community.import"), "", tr("community.filter"))
        if not path:
            return
        result = import_file(path)
        if result is None:
            QMessageBox.warning(self, tr("dialog.title"), tr("community.invalid"))
            return
        _, _, settings = result
        self._store.apply(settings)
        QMessageBox.information(self, tr("dialog.title"), tr("community.imported"))

    # -------------------------------------------------------------- export
    def _on_export(self) -> None:
        settings = self._store.get()
        name, ok = QInputDialog.getText(self, tr("button.export"), tr("community.name"))
        if not ok:
            return
        default_name = f"crossac-{settings.style}"
        path, _ = QFileDialog.getSaveFileName(
            self, tr("button.export"), default_name, tr("community.filter"))
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        if export_settings(settings, path, name or default_name):
            QMessageBox.information(self, tr("dialog.title"), tr("community.exported"))
        else:
            QMessageBox.warning(self, tr("dialog.title"), tr("community.export_error"))

    # -------------------------------------------------------------- controls
    def _add_slider(self, grid: QGridLayout, row: int, key: str, low: int, high: int) -> None:
        label = QLabel()
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(low, high)
        value = QLabel()
        value.setObjectName("valueLabel")
        value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        value.setMinimumWidth(38)

        def on_change(v: int) -> None:
            value.setText(str(v))
            self._store.set(**{key: v})

        slider.valueChanged.connect(on_change)
        grid.addWidget(label, row, 0)
        grid.addWidget(slider, row, 1)
        grid.addWidget(value, row, 2)
        self._sliders[key] = slider
        self._value_labels[key] = value
        self._control_labels[key] = label

    def _add_color(self, grid: QGridLayout, row: int, key: str) -> None:
        label = QLabel()
        btn = QPushButton()
        btn.setObjectName("colorButton")
        btn.setMaximumWidth(70)

        def on_click() -> None:
            current = QColor(self._store.get().__getattribute__(key))
            color = QColorDialog.getColor(current, self, tr("setting.color"))
            if color.isValid():
                self._store.set(**{key: color.name().upper()})

        def paint_swatch() -> None:
            btn.setStyleSheet(
                f"background-color: {self._store.get().__getattribute__(key)};"
                f"border: 1px solid #3a3f4a;"
            )

        btn.clicked.connect(on_click)
        self._store.changed.connect(paint_swatch)
        paint_swatch()
        grid.addWidget(label, row, 0)
        grid.addWidget(btn, row, 1)
        self._color_buttons[key] = btn
        self._control_labels[key] = label

    def _add_cap(self, grid: QGridLayout, row: int) -> None:
        label = QLabel()
        combo = QComboBox()
        for cap in CAPS:
            combo.addItem(tr(f"cap.{cap}"), cap)
        combo.currentIndexChanged.connect(
            lambda i: self._store.set(cap=combo.itemData(i)) if i >= 0 else None)
        grid.addWidget(label, row, 0)
        grid.addWidget(combo, row, 1)
        self._cap_combo = combo
        self._control_labels["cap"] = label

    def _pick_outline_color(self) -> None:
        current = QColor(self._store.get().outline_color)
        color = QColorDialog.getColor(current, self, tr("setting.outline_color"))
        if color.isValid():
            self._store.set(outline_color=color.name().upper())

    def _pick_dot_color(self) -> None:
        current = QColor(self._store.get().dot_color)
        color = QColorDialog.getColor(current, self, tr("setting.dot_color"))
        if color.isValid():
            self._store.set(dot_color=color.name().upper())

    def _populate_monitors(self) -> None:
        self._monitor_combo.blockSignals(True)
        self._monitor_combo.clear()
        screens = QApplication.screens()
        for i in range(len(screens)):
            if i == 0:
                self._monitor_combo.addItem(tr("monitor.primary"), i)
            else:
                name = screens[i].name() or f"Monitor {i + 1}"
                self._monitor_combo.addItem(f"{name} ({i + 1})", i)
        self._monitor_combo.blockSignals(False)

    def _on_monitor_changed(self, index: int) -> None:
        if index >= 0:
            self._store.set(monitor=self._monitor_combo.itemData(index))

    def _rebuild_language_combo(self) -> None:
        self._language_combo.blockSignals(True)
        self._language_combo.clear()
        self._language_combo.addItem(tr("language.auto"), "")
        for code in get_i18n().available_locales():
            self._language_combo.addItem(get_i18n().locale_name(code), code)
        self._language_combo.blockSignals(False)

    def _on_language_changed(self, index: int) -> None:
        code = self._language_combo.itemData(index)
        i18n = get_i18n()
        if code:
            i18n.set_locale(code)
        else:
            i18n.set_locale(i18n.system_locale())
        self._store.set(language=code)
        self._retranslate()

    # ------------------------------------------------------------ translation
    def _retranslate(self) -> None:
        self.setWindowTitle(tr("dialog.title"))
        self._subtitle.setText(tr("app.subtitle"))
        self._hint.setText(tr("hint.fullscreen"))

        tabs = self.findChild(QTabWidget)
        if tabs is not None:
            tabs.setTabText(0, tr("tab.crosshair"))
            tabs.setTabText(1, tr("tab.community"))

        key_map = {
            "size": "setting.size",
            "size_v": "setting.size_v",
            "gap": "setting.gap",
            "gap_v": "setting.gap_v",
            "thickness": "setting.thickness",
            "rotation": "setting.rotation",
            "opacity": "setting.opacity",
            "offset_x": "setting.offset_x",
            "offset_y": "setting.offset_y",
            "color": "setting.color",
            "dot_size": "setting.dot_size",
            "outline_thickness": "setting.outline_thickness",
            "sides": "setting.sides",
            "cap": "setting.cap",
        }
        for key, label in self._control_labels.items():
            label.setText(tr(key_map.get(key, key)))

        for btn, style in zip(self._style_buttons, STYLES):
            btn.setToolTip(tr(f"style.{style}"))

        self._appearance_box.setTitle(tr("category.appearance"))
        self._arms_box.setTitle(tr("setting.arms"))
        self._sides_box.setTitle(tr("category.sides"))
        self._reticle_box.setTitle(tr("category.reticle"))
        self._outline_box.setTitle(tr("category.outline"))
        self._display_box.setTitle(tr("category.display"))
        self._dot_check.setText(tr("setting.center_dot"))
        self._outline_check.setText(tr("setting.outline"))
        self._monitor_label.setText(tr("setting.monitor"))
        self._language_label.setText(tr("setting.language"))
        for letter, _ in _ARMS_LABELS:
            self._arm_checks[letter].setText(tr(dict(_ARMS_LABELS)[letter]))
        self._cap_combo.blockSignals(True)
        for i in range(self._cap_combo.count()):
            self._cap_combo.setItemText(i, tr(f"cap.{self._cap_combo.itemData(i)}"))
        self._cap_combo.blockSignals(False)
        self._refresh_btn.setText(tr("community.refresh"))
        self._import_btn.setText(tr("community.import"))
        self._export_btn.setText(tr("button.export"))
        self._reset_btn.setText(tr("button.reset"))
        self._close_btn.setText(tr("button.close"))
        self._set_community_note(tr("community.note"))
        self._set_community_status(tr("community.loading"))
        self._populate_monitors()

        # keep the selected language
        self._language_combo.blockSignals(True)
        current = self._store.get().language
        index = self._language_combo.findData(current)
        self._language_combo.setCurrentIndex(index if index >= 0 else 0)
        self._language_combo.blockSignals(False)

    # ------------------------------------------------------------------ sync
    def _sync_controls(self) -> None:
        s = self._store.get()
        for key, slider in self._sliders.items():
            slider.blockSignals(True)
            slider.setValue(getattr(s, key))
            slider.blockSignals(False)
            self._value_labels[key].setText(str(getattr(s, key)))
        for key, btn in self._color_buttons.items():
            btn.setStyleSheet(
                f"background-color: {getattr(s, key)}; border: 1px solid #3a3f4a;"
            )
        self._dot_check.blockSignals(True)
        self._dot_check.setChecked(s.center_dot)
        self._dot_check.blockSignals(False)
        self._outline_check.blockSignals(True)
        self._outline_check.setChecked(s.outline)
        self._outline_check.blockSignals(False)
        self._dot_color_btn.setStyleSheet(
            f"background-color: {s.dot_color}; border: 1px solid #3a3f4a;"
        )
        self._outline_color_btn.setStyleSheet(
            f"background-color: {s.outline_color}; border: 1px solid #3a3f4a;"
        )
        for letter, _ in _ARMS_LABELS:
            self._arm_checks[letter].blockSignals(True)
            self._arm_checks[letter].setChecked(letter in s.arms)
            self._arm_checks[letter].blockSignals(False)
        self._cap_combo.blockSignals(True)
        index = self._cap_combo.findData(s.cap)
        self._cap_combo.setCurrentIndex(index if index >= 0 else 0)
        self._cap_combo.blockSignals(False)
        self._monitor_combo.blockSignals(True)
        for i in range(self._monitor_combo.count()):
            if self._monitor_combo.itemData(i) == s.monitor:
                self._monitor_combo.setCurrentIndex(i)
                break
        self._monitor_combo.blockSignals(False)
        for btn, style in zip(self._style_buttons, STYLES):
            btn.blockSignals(True)
            btn.setChecked(style == s.style)
            btn.blockSignals(False)

    def _on_reset(self) -> None:
        answer = QMessageBox.question(
            self, tr("button.reset"), tr("reset.confirm"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self._store.reset()
            self._sync_controls()
