"""Global dark theme applied to the whole application."""

DARK_QSS = """
QWidget {
    background-color: #17181c;
    color: #e6e6e6;
    font-family: "Segoe UI", "Helvetica Neue", "SF Pro Text", sans-serif;
    font-size: 13px;
}
QDialog, QMainWindow {
    background-color: #17181c;
}

/* ------------------------------------------------------------ group boxes */
QGroupBox {
    border: 1px solid #2a2d35;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 8px;
    font-weight: 600;
    color: #9aa0ae;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    background-color: #17181c;
}

/* --------------------------------------------------------------- sliders */
QSlider::groove:horizontal {
    height: 4px;
    background: #2a2d35;
    border-radius: 2px;
}
QSlider::sub-page:horizontal {
    background: #00ff88;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #f0f0f0;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #ffffff;
}

/* ------------------------------------------------------------ comboboxes */
QComboBox {
    background-color: #22242b;
    border: 1px solid #2a2d35;
    border-radius: 6px;
    padding: 5px 10px;
    min-height: 18px;
}
QComboBox:hover {
    border-color: #3a3f4a;
}
QComboBox::drop-down {
    border: none;
    width: 22px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #9aa0ae;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #22242b;
    border: 1px solid #2a2d35;
    selection-background-color: #00ff88;
    selection-color: #111;
    outline: none;
}

/* -------------------------------------------------------------- checkboxes */
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #3a3f4a;
    background-color: #22242b;
}
QCheckBox::indicator:checked {
    background-color: #00ff88;
    border-color: #00ff88;
    image: none;
}

/* ---------------------------------------------------------------- buttons */
QPushButton, QToolButton {
    background-color: #22242b;
    border: 1px solid #2a2d35;
    border-radius: 6px;
    padding: 7px 14px;
    color: #e6e6e6;
}
QPushButton:hover, QToolButton:hover {
    background-color: #2a2d35;
    border-color: #3a3f4a;
}
QPushButton:pressed, QToolButton:pressed {
    background-color: #1d1f24;
}
QPushButton#primaryButton {
    background-color: #00ff88;
    color: #0d0d0f;
    font-weight: 700;
    border: none;
}
QPushButton#primaryButton:hover {
    background-color: #2bff9b;
}
QPushButton#dangerButton {
    color: #ff6b6b;
}

/* ---------------------------------------------------------- style buttons */
QToolButton#styleButton {
    border: 2px solid #2a2d35;
    border-radius: 8px;
    padding: 6px;
    background-color: #1d1f24;
}
QToolButton#styleButton:checked {
    border-color: #00ff88;
    background-color: #20251f;
}
QToolButton#styleButton:hover:!checked {
    border-color: #3a3f4a;
}

/* ------------------------------------------------------------ color swatch */
QPushButton#colorButton {
    border: none;
    border-radius: 6px;
    min-width: 34px;
    min-height: 26px;
}

/* --------------------------------------------------------------- preview */
QWidget#previewPanel {
    background-color: #0f1013;
    border: 1px solid #2a2d35;
    border-radius: 10px;
}

/* ----------------------------------------------------------- value labels */
QLabel#valueLabel {
    color: #00ff88;
    font-weight: 600;
}
QLabel#hintLabel {
    color: #6f7686;
    font-size: 12px;
}

/* ---------------------------------------------------------------- menus */
QMenu {
    background-color: #22242b;
    border: 1px solid #2a2d35;
    border-radius: 8px;
    padding: 6px;
}
QMenu::item {
    padding: 6px 22px;
    border-radius: 5px;
}
QMenu::item:selected {
    background-color: #00ff88;
    color: #0d0d0f;
}
QMenu::separator {
    height: 1px;
    background: #2a2d35;
    margin: 4px 8px;
}

/* --------------------------------------------------------------- toolbar */
QToolBar {
    background-color: #1d1f24;
    border: none;
    padding: 2px;
}
QStatusBar {
    background-color: #17181c;
    color: #6f7686;
}

/* ------------------------------------------------------------- tooltips */
QToolTip {
    background-color: #2a2d35;
    color: #e6e6e6;
    border: 1px solid #3a3f4a;
    padding: 4px 8px;
    border-radius: 4px;
}
"""
