ACCENT = "#7DA6F5"
ACCENT_RGB = (125, 166, 245)

DARK_QSS = f"""
QWidget {{
    color: #E9EDF3;
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 13px;
    selection-background-color: rgba(125, 166, 245, 0.28);
    selection-color: #0C1220;
}}

QDialog {{
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #121722,
        stop: 0.45 #0D1119,
        stop: 1 #0A0C11
    );
}}
QToolTip {{
    background-color: rgba(21, 25, 34, 0.95);
    color: #D9DEE8;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-top-color: rgba(255, 255, 255, 0.22);
    padding: 6px 10px;
    border-radius: 8px;
}}

QLabel#appTitle {{
    font-size: 24px;
    font-weight: 300;
    letter-spacing: 5px;
    color: #F4F1EA;
}}
QLabel#appSubtitle {{
    color: #7C8698;
    font-size: 12px;
    letter-spacing: 0.3px;
}}
QFrame#headerLine {{
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 rgba(125, 166, 245, 0.0),
        stop: 0.5 rgba(125, 166, 245, 0.45),
        stop: 1 rgba(125, 166, 245, 0.0));
    border: none;
}}

QTabWidget::pane {{
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 18px;
    top: -1px;
    background-color: rgba(255, 255, 255, 0.015);
}}
QTabBar::tab {{
    background: transparent;
    color: #8B95A6;
    padding: 11px 22px;
    margin-right: 6px;
    border: none;
    border-radius: 12px;
    font-weight: 500;
}}
QTabBar::tab:hover:!selected {{
    color: #D9DEE8;
    background-color: rgba(255, 255, 255, 0.05);
}}
QTabBar::tab:selected {{
    color: #F2F4F8;
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(125, 166, 245, 0.22),
        stop: 1 rgba(125, 166, 245, 0.06));
    border: 1px solid rgba(125, 166, 245, 0.3);
    border-top-color: rgba(140, 180, 250, 0.55);
    font-weight: 600;
}}
QTabBar::tab:focus {{ outline: none; }}

QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
QWidget#scrollBody {{
    background: transparent;
}}

QGroupBox {{
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(255, 255, 255, 0.06),
        stop: 1 rgba(255, 255, 255, 0.02));
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-top-color: rgba(255, 255, 255, 0.16);
    border-radius: 16px;
    margin-top: 20px;
    padding: 18px 16px 14px 16px;
    font-weight: 500;
    color: #C9D0DA;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    background-color: transparent;
    color: #99A3B5;
    font-size: 10px;
    letter-spacing: 1.4px;
    font-weight: 600;
}}

QSlider::groove:horizontal {{
    height: 3px;
    background: rgba(255, 255, 255, 0.09);
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: rgba(125, 166, 245, 0.6);
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 7px;
    background: #F5F2EA;
    border: 1px solid rgba(0, 0, 0, 0.35);
}}
QSlider::handle:horizontal:hover {{
    background: #FFFFFF;
}}
QSlider::handle:horizontal:pressed {{
    background: {ACCENT};
}}

QComboBox, QLineEdit {{
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(255, 255, 255, 0.1),
        stop: 1 rgba(255, 255, 255, 0.035));
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-top-color: rgba(255, 255, 255, 0.17);
    border-radius: 10px;
    padding: 7px 12px;
    color: #E9EDF3;
    min-height: 16px;
}}
QComboBox:hover, QLineEdit:hover {{
    border-color: rgba(255, 255, 255, 0.18);
}}
QComboBox:focus, QLineEdit:focus {{
    border-color: rgba(125, 166, 245, 0.55);
}}
QComboBox::drop-down {{
    border: none;
    width: 26px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #8B95A6;
    margin-right: 9px;
}}
QComboBox QAbstractItemView {{
    background-color: #151A24;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 5px;
    selection-background-color: rgba(125, 166, 245, 0.22);
    selection-color: #EFF3FF;
    outline: none;
}}
QComboBox QAbstractItemView::item {{
    min-height: 26px;
    border-radius: 7px;
    padding: 2px 9px;
}}

QCheckBox {{
    spacing: 9px;
    color: #C9D0DA;
}}
QCheckBox:hover {{ color: #E9EDF3; }}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 5px;
    border: 1px solid rgba(255, 255, 255, 0.24);
    background-color: rgba(255, 255, 255, 0.04);
}}
QCheckBox::indicator:hover {{
    border-color: rgba(125, 166, 245, 0.7);
}}
QCheckBox::indicator:checked {{
    background-color: rgba(125, 166, 245, 0.9);
    border-color: rgba(125, 166, 245, 0.95);
    image: none;
}}

QPushButton, QToolButton {{
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-top-color: rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    padding: 8px 16px;
    color: #E2E6ED;
    font-weight: 500;
}}
QPushButton:hover, QToolButton:hover {{
    background-color: rgba(255, 255, 255, 0.09);
    border-color: rgba(255, 255, 255, 0.17);
}}
QPushButton:pressed, QToolButton:pressed {{
    background-color: rgba(255, 255, 255, 0.02);
}}
QPushButton:disabled, QToolButton:disabled {{
    color: rgba(255, 255, 255, 0.3);
    background-color: rgba(255, 255, 255, 0.015);
}}
QPushButton#primaryButton {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #6E9DF4, stop: 1 #97C0FA);
    color: #0C1424;
    font-weight: 600;
    border: none;
    padding: 8px 18px;
}}
QPushButton#primaryButton:hover {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #7DAAF7, stop: 1 #A8C8FB);
}}
QPushButton#primaryButton:pressed {{
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #5F8CEB, stop: 1 #7DA6F5);
}}
QPushButton#dangerButton {{
    background-color: transparent;
    border: 1px solid rgba(255, 122, 142, 0.3);
    color: #E5A4B0;
}}
QPushButton#dangerButton:hover {{
    background-color: rgba(255, 122, 142, 0.1);
    border-color: rgba(255, 122, 142, 0.55);
}}

QWidget#styleBar {{
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 rgba(255, 255, 255, 0.05),
        stop: 1 rgba(255, 255, 255, 0.02));
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-top-color: rgba(255, 255, 255, 0.16);
    border-radius: 16px;
    padding: 5px;
}}
QToolButton#styleButton {{
    background: transparent;
    border: none;
    border-radius: 11px;
    padding: 7px 4px;
    color: #8B95A6;
}}
QToolButton#styleButton:hover:!checked {{
    background-color: rgba(255, 255, 255, 0.055);
    color: #D9DEE8;
}}
QToolButton#styleButton:checked {{
    background-color: rgba(125, 166, 245, 0.12);
    border: 1px solid rgba(125, 166, 245, 0.45);
    color: #C9DBFF;
}}

QToolButton#colorButton {{
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 7px;
    min-width: 36px;
    min-height: 26px;
}}
QToolButton#colorButton:hover {{
    border-color: rgba(125, 166, 245, 0.8);
}}
QToolButton#swatchButton {{
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 7px;
    padding: 0;
}}
QToolButton#swatchButton:hover {{
    border: 2px solid rgba(255, 255, 255, 0.85);
}}
QFrame#colorPopup {{
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #1A2030, stop: 1 #11151F);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-top-color: rgba(255, 255, 255, 0.22);
    border-radius: 16px;
}}
QLabel#popupTitle {{
    color: #99A3B5;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.2px;
}}

QWidget#previewPanel {{
    background-color: transparent;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-top-color: rgba(255, 255, 255, 0.16);
    border-radius: 16px;
}}

QLabel#valueLabel {{
    color: #A9C0F7;
    font-weight: 500;
}}
QLabel#hintLabel {{
    color: #7C8698;
    font-size: 12px;
}}

QListWidget {{
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 16px;
    padding: 6px;
    outline: none;
}}
QListWidget::item {{
    border-radius: 10px;
    padding: 8px 10px;
    color: #C9D0DA;
}}
QListWidget::item:hover {{
    background-color: rgba(255, 255, 255, 0.055);
}}
QListWidget::item:selected {{
    background-color: rgba(125, 166, 245, 0.14);
    border: 1px solid rgba(125, 166, 245, 0.4);
    color: #EAF0FF;
}}

QMenu {{
    background-color: rgba(21, 25, 34, 0.96);
    border: 1px solid rgba(255, 255, 255, 0.11);
    border-radius: 14px;
    padding: 6px;
}}
QMenu::item {{
    padding: 8px 26px;
    border-radius: 8px;
    color: #D9DEE8;
}}
QMenu::item:selected {{
    background-color: rgba(125, 166, 245, 0.2);
    color: #EAF0FF;
}}
QMenu::item:disabled {{
    color: rgba(255, 255, 255, 0.3);
}}
QMenu::separator {{
    height: 1px;
    background: rgba(255, 255, 255, 0.09);
    margin: 6px 12px;
}}
QMenu::icon {{
    padding-right: 8px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 9px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 0.13);
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(125, 166, 245, 0.45);
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 9px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: rgba(255, 255, 255, 0.13);
    border-radius: 5px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: rgba(125, 166, 245, 0.45);
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0;
    width: 0;
}}
QScrollBar::add-page, QScrollBar::sub-page {{
    background: transparent;
}}

QToolBar {{
    background-color: rgba(255, 255, 255, 0.03);
    border: none;
    padding: 2px;
}}
QStatusBar {{
    background-color: transparent;
    color: #7C8698;
}}
"""
