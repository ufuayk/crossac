#!/usr/bin/env bash

set -euo pipefail

APP_NAME="Crossac"
BIN_NAME="crossac"

if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    echo "Do not run this uninstaller as root or with sudo." >&2
    echo "Crossac is installed per-user, run this as the same user who installed it." >&2
    exit 1
fi

OS="$(uname -s)"

if [[ "$OS" == "Darwin" ]]; then
    INSTALL_DIR="$HOME/Library/Application Support/Crossac"
    APPS_DIR="$HOME/Applications"
    APP_BUNDLE="$APPS_DIR/${APP_NAME}.app"
    BIN_DIR="$HOME/.local/bin"
elif [[ "$OS" == "Linux" ]]; then
    INSTALL_DIR="$HOME/.local/share/crossac"
    BIN_DIR="$HOME/.local/bin"
    DESKTOP_DIR="$HOME/.local/share/applications"
    ICON_DIR="$HOME/.local/share/icons/hicolor/512x512/apps"
else
    echo "This uninstaller only supports macOS and Linux. Detected: $OS" >&2
    exit 1
fi

c_reset="\033[0m"
c_green="\033[32m"
c_blue="\033[34m"
c_yellow="\033[33m"

info() { printf "${c_blue}==>${c_reset} %s\n" "$1"; }
ok()   { printf "${c_green}==>${c_reset} %s\n" "$1"; }
warn() { printf "${c_yellow}==>${c_reset} %s\n" "$1"; }

FOUND_SOMETHING=0

info "Uninstalling Crossac..."

if [[ "$OS" == "Darwin" ]]; then
    if [[ -d "$APP_BUNDLE" ]]; then
        rm -rf "$APP_BUNDLE"
        ok "Removed app: $APP_BUNDLE"
        FOUND_SOMETHING=1
    fi
else
    if [[ -f "$DESKTOP_DIR/${BIN_NAME}.desktop" ]]; then
        rm -f "$DESKTOP_DIR/${BIN_NAME}.desktop"
        ok "Removed application menu entry"
        FOUND_SOMETHING=1
    fi
    if [[ -f "$ICON_DIR/${BIN_NAME}.png" ]]; then
        rm -f "$ICON_DIR/${BIN_NAME}.png"
        ok "Removed icon"
        FOUND_SOMETHING=1
    fi
    command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
    command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi

if [[ -f "$BIN_DIR/$BIN_NAME" ]]; then
    rm -f "$BIN_DIR/$BIN_NAME"
    ok "Removed CLI shortcut: $BIN_DIR/$BIN_NAME"
    FOUND_SOMETHING=1
fi

if [[ -d "$INSTALL_DIR" ]]; then
    rm -rf "$INSTALL_DIR"
    ok "Removed program files: $INSTALL_DIR"
    FOUND_SOMETHING=1
fi

echo
if [[ "$FOUND_SOMETHING" -eq 1 ]]; then
    ok "Crossac has been uninstalled."
else
    warn "No Crossac installation was found on this system."
fi
