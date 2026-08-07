import sys

from PySide6.QtWidgets import QApplication

from app.config import SettingsStore
from app.i18n import init_i18n
from app.overlay import OverlayWindow
from app.settings_dialog import SettingsDialog
from app.theme import DARK_QSS
from app.tray import TrayIcon


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Crossac")
    app.setOrganizationName("Crossac")
    app.setApplicationDisplayName("Crossac")
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(DARK_QSS)

    store = SettingsStore()

    stored_language = store.get().language or None
    init_i18n(stored_language)

    overlay = OverlayWindow(store)
    dialog = SettingsDialog(store)
    tray = TrayIcon(store, overlay, dialog)

    overlay.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
