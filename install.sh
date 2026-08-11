#!/usr/bin/env bash

set -euo pipefail

REPO_URL="https://github.com/ufuayk/crossac.git"
APP_NAME="Crossac"
BIN_NAME="crossac"

if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    echo "Do not run this installer as root or with sudo." >&2
    echo "It installs Crossac for your own user account only." >&2
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
    echo "This installer only supports macOS and Linux. Detected: $OS" >&2
    echo "Windows support is coming later." >&2
    exit 1
fi

c_reset="\033[0m"
c_bold="\033[1m"
c_green="\033[32m"
c_yellow="\033[33m"
c_red="\033[31m"
c_blue="\033[34m"

info()  { printf "${c_blue}==>${c_reset} %s\n" "$1"; }
ok()    { printf "${c_green}==>${c_reset} %s\n" "$1"; }
warn()  { printf "${c_yellow}==>${c_reset} %s\n" "$1"; }
err()   { printf "${c_red}==>${c_reset} %s\n" "$1" >&2; }

need_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        err "'$1' not found. Please install it first: $2"
        exit 1
    fi
}

CLONED_FRESH=0
INSTALL_SUCCEEDED=0

cleanup_on_failure() {
    local status=$?
    if [[ $status -ne 0 && $INSTALL_SUCCEEDED -eq 0 && $CLONED_FRESH -eq 1 ]]; then
        err "Installation failed, rolling back partial install..."
        rm -rf "$INSTALL_DIR"
    fi
    exit "$status"
}
trap cleanup_on_failure EXIT

info "Installing Crossac ($OS)..."

need_cmd git "https://git-scm.com"
need_cmd curl "https://curl.se"

PYTHON_BIN=""
for candidate in python3.13 python3.12 python3.11 python3.10 python3.9 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        ver="$("$candidate" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "0.0")"
        major="${ver%%.*}"
        minor="${ver##*.}"
        if [[ "$major" -eq 3 && "$minor" -ge 9 ]]; then
            PYTHON_BIN="$candidate"
            break
        fi
    fi
done

if [[ -z "$PYTHON_BIN" ]]; then
    err "Python 3.9+ not found."
    if [[ "$OS" == "Darwin" ]]; then
        err "Install it with: brew install python3   (or https://python.org)"
    else
        err "Install it with your distro's package manager, e.g. sudo apt install python3 python3-venv"
    fi
    exit 1
fi

ok "Found Python: $($PYTHON_BIN --version)"

if ! "$PYTHON_BIN" -m venv --help >/dev/null 2>&1; then
    err "'python3-venv' appears to be missing."
    err "Debian/Ubuntu: sudo apt install python3-venv"
    exit 1
fi

if [[ -e "$INSTALL_DIR" && ! -d "$INSTALL_DIR/.git" ]]; then
    err "$INSTALL_DIR exists and doesn't look like a Crossac install. Refusing to overwrite it."
    err "Remove or rename it manually, then re-run this script."
    exit 1
fi

mkdir -p "$(dirname "$INSTALL_DIR")"

if [[ -d "$INSTALL_DIR/.git" ]]; then
    info "Existing install found, updating..."
    git -C "$INSTALL_DIR" remote set-url origin "$REPO_URL"
    git -C "$INSTALL_DIR" fetch --depth 1 origin
    DEFAULT_BRANCH="$(git -C "$INSTALL_DIR" remote show origin | sed -n '/HEAD branch/s/.*: //p')"
    git -C "$INSTALL_DIR" reset --hard "origin/${DEFAULT_BRANCH:-main}"
    git -C "$INSTALL_DIR" clean -fdx -e .venv -e .installer_icon
else
    info "Downloading source code..."
    CLONED_FRESH=1
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi
ok "Source ready: $INSTALL_DIR"

chmod 700 "$INSTALL_DIR"

VENV_DIR="$INSTALL_DIR/.venv"

if [[ ! -d "$VENV_DIR" ]]; then
    info "Creating isolated virtual environment..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

VENV_PY="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

if [[ ! -f "$INSTALL_DIR/requirements.txt" ]]; then
    err "requirements.txt not found in the repository. Aborting."
    exit 1
fi

info "Installing dependencies into the venv..."
"$VENV_PY" -m pip install --upgrade pip --quiet
"$VENV_PIP" install --quiet --index-url https://pypi.org/simple -r "$INSTALL_DIR/requirements.txt"
ok "Dependencies installed."

info "Generating app icon..."

ICON_SRC_DIR="$INSTALL_DIR/.installer_icon"
mkdir -p "$ICON_SRC_DIR"

"$VENV_PY" - "$ICON_SRC_DIR" <<'PYEOF'
import sys
from pathlib import Path
from PySide6.QtGui import QImage, QPainter, QPen, QColor
from PySide6.QtCore import Qt

out_dir = Path(sys.argv[1])
out_dir.mkdir(parents=True, exist_ok=True)

def make_icon(size: int) -> QImage:
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)

    cx, cy = size / 2, size / 2
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(24, 26, 30, 255))
    radius = size * 0.22
    p.drawRoundedRect(0, 0, size, size, radius, radius)

    pen = QPen(QColor(80, 220, 120, 255))
    pen.setWidthF(size * 0.055)
    pen.setCapStyle(Qt.RoundCap)
    p.setPen(pen)

    length = size * 0.30
    gap = size * 0.12

    p.drawLine(cx, cy - gap - length, cx, cy - gap)
    p.drawLine(cx, cy + gap, cx, cy + gap + length)
    p.drawLine(cx - gap - length, cy, cx - gap, cy)
    p.drawLine(cx + gap, cy, cx + gap + length, cy)

    dot_pen = QPen(QColor(80, 220, 120, 255))
    dot_pen.setWidthF(1)
    p.setPen(dot_pen)
    p.setBrush(QColor(80, 220, 120, 255))
    r = size * 0.035
    p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

    p.end()
    return img

for size in (16, 32, 64, 128, 256, 512, 1024):
    make_icon(size).save(str(out_dir / f"icon_{size}.png"))

print("icons written")
PYEOF

ok "Icon generated."

if [[ "$OS" == "Darwin" ]]; then
    info "Building Crossac.app..."
    mkdir -p "$APPS_DIR"
    rm -rf "$APP_BUNDLE"
    mkdir -p "$APP_BUNDLE/Contents/MacOS" "$APP_BUNDLE/Contents/Resources"

    ICONSET="$ICON_SRC_DIR/AppIcon.iconset"
    mkdir -p "$ICONSET"
    cp "$ICON_SRC_DIR/icon_16.png"   "$ICONSET/icon_16x16.png"
    cp "$ICON_SRC_DIR/icon_32.png"   "$ICONSET/icon_16x16@2x.png"
    cp "$ICON_SRC_DIR/icon_32.png"   "$ICONSET/icon_32x32.png"
    cp "$ICON_SRC_DIR/icon_64.png"   "$ICONSET/icon_32x32@2x.png"
    cp "$ICON_SRC_DIR/icon_128.png"  "$ICONSET/icon_128x128.png"
    cp "$ICON_SRC_DIR/icon_256.png"  "$ICONSET/icon_128x128@2x.png"
    cp "$ICON_SRC_DIR/icon_256.png"  "$ICONSET/icon_256x256.png"
    cp "$ICON_SRC_DIR/icon_512.png"  "$ICONSET/icon_256x256@2x.png"
    cp "$ICON_SRC_DIR/icon_512.png"  "$ICONSET/icon_512x512.png"
    cp "$ICON_SRC_DIR/icon_1024.png" "$ICONSET/icon_512x512@2x.png"

    if command -v iconutil >/dev/null 2>&1; then
        iconutil -c icns "$ICONSET" -o "$APP_BUNDLE/Contents/Resources/AppIcon.icns"
    else
        cp "$ICON_SRC_DIR/icon_512.png" "$APP_BUNDLE/Contents/Resources/AppIcon.icns"
    fi

    cat > "$APP_BUNDLE/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.crossac.crossac</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleExecutable</key>
    <string>crossac-launcher</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon.icns</string>
    <key>LSUIElement</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
</dict>
</plist>
PLIST

    cat > "$APP_BUNDLE/Contents/MacOS/crossac-launcher" <<LAUNCH
#!/usr/bin/env bash
exec "$VENV_PY" "$INSTALL_DIR/main.py"
LAUNCH
    chmod +x "$APP_BUNDLE/Contents/MacOS/crossac-launcher"

    ok "Crossac.app built: $APP_BUNDLE"

    touch "$APP_BUNDLE"
fi

if [[ "$OS" == "Linux" ]]; then
    info "Installing application menu shortcut..."
    mkdir -p "$DESKTOP_DIR" "$ICON_DIR"
    cp "$ICON_SRC_DIR/icon_512.png" "$ICON_DIR/${BIN_NAME}.png"

    cat > "$DESKTOP_DIR/${BIN_NAME}.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=${APP_NAME}
Comment=Lightweight on-screen crosshair overlay
Exec=${VENV_PY} ${INSTALL_DIR}/main.py
Icon=${BIN_NAME}
Terminal=false
Categories=Utility;Game;
StartupNotify=true
DESKTOP

    chmod +x "$DESKTOP_DIR/${BIN_NAME}.desktop"

    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
    fi
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
    fi

    ok "Added to application menu (search for Crossac)."
fi

mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/$BIN_NAME" <<CLI
#!/usr/bin/env bash
exec "$VENV_PY" "$INSTALL_DIR/main.py" "\$@"
CLI
chmod +x "$BIN_DIR/$BIN_NAME"

INSTALL_SUCCEEDED=1

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    warn "$BIN_DIR is not on your PATH. To run 'crossac' from a terminal,"
    warn "  add this to your shell config (~/.zshrc / ~/.bashrc):"
    warn "  export PATH=\"$BIN_DIR:\$PATH\""
fi

echo
ok "Installation complete!"
if [[ "$OS" == "Darwin" ]]; then
    echo "  -> Open it from Launchpad or ${c_bold}${APPS_DIR}/${APP_NAME}.app${c_reset}"
else
    echo "  -> Search for 'Crossac' in your application menu to open it."
fi
echo "  -> Or from a terminal: $BIN_DIR/$BIN_NAME"
echo
echo "To uninstall, run:"
echo "  curl -fsSL https://raw.githubusercontent.com/ufuayk/crossac/main/uninstall.sh | bash"
