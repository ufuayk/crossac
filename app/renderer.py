from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap, QPolygonF

from .config import ARMS_LETTERS, CAPS, CrosshairSettings

STYLES = ("cross", "circle", "dot")

_CAP_STYLES = {
    "flat": Qt.PenCapStyle.FlatCap,
    "round": Qt.PenCapStyle.RoundCap,
    "square": Qt.PenCapStyle.SquareCap,
}


def _half_extent(s: CrosshairSettings) -> float:
    outline = s.outline_thickness if s.outline else 0
    if s.style == "dot":
        return s.dot_size + outline + 2
    if s.style == "circle":
        return s.gap + s.size / 2.0 + s.thickness / 2.0 + outline
    h = max(s.gap + s.size, s.gap_v + s.size_v)
    return h + s.thickness / 2.0 + outline


def _pen(color: str, width: float, cap: str) -> QPen:
    pen = QPen(QColor(color), width)
    pen.setCapStyle(_CAP_STYLES.get(cap, Qt.PenCapStyle.FlatCap))
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def _stroke(painter: QPainter, s: CrosshairSettings, width: float, draw: "callable") -> None:
    if s.outline:
        painter.setPen(_pen(s.outline_color, width + 2.0 * s.outline_thickness, s.cap))
        draw()
    painter.setPen(_pen(s.color, width, s.cap))
    draw()


def _stroke_lines(painter, s, lines) -> None:
    for x1, y1, x2, y2 in lines:
        _stroke(painter, s, s.thickness, lambda x1=x1, y1=y1, x2=x2, y2=y2: painter.drawLine(x1, y1, x2, y2))


def _draw_cross(painter: QPainter, s: CrosshairSettings) -> None:
    h_end, v_end = s.gap + s.size, s.gap_v + s.size_v
    arms = set(s.arms)
    lines = []
    if "r" in arms:
        lines.append((s.gap, 0.0, h_end, 0.0))
    if "l" in arms:
        lines.append((-s.gap, 0.0, -h_end, 0.0))
    if "b" in arms:
        lines.append((0.0, s.gap_v, 0.0, v_end))
    if "t" in arms:
        lines.append((0.0, -s.gap_v, 0.0, -v_end))
    _stroke_lines(painter, s, lines)


def _draw_polygon(painter: QPainter, s: CrosshairSettings) -> None:
    n = max(3, s.sides)
    radius = s.gap + s.size / 2.0
    points = QPolygonF()
    for i in range(n):
        angle = 2.0 * math.pi * i / n
        points.append(QPointF(radius * math.cos(angle), radius * math.sin(angle)))
    _stroke(painter, s, s.thickness, lambda: painter.drawPolygon(points))


def _draw_dot(painter: QPainter, s: CrosshairSettings, radius: float, color: str) -> None:
    if s.outline:
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(s.outline_color))
        painter.drawEllipse(QRectF(-radius - s.outline_thickness, -radius - s.outline_thickness,
                                   2 * (radius + s.outline_thickness), 2 * (radius + s.outline_thickness)))
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(color))
    painter.drawEllipse(QRectF(-radius, -radius, radius * 2, radius * 2))


def render_pixmap(s: CrosshairSettings, dpr: float = 1.0) -> QPixmap:
    scale = max(dpr, 1.0)
    half = _half_extent(s) * scale
    side = max(int(math.ceil(2 * (half + 4))), 1)

    pixmap = QPixmap(side, side)
    pixmap.setDevicePixelRatio(scale)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.translate(side / 2.0, side / 2.0)
    painter.scale(scale, scale)
    painter.rotate(s.rotation)
    painter.setOpacity(s.opacity / 100.0)

    if s.style == "circle":
        _draw_polygon(painter, s)
    elif s.style == "dot":
        _draw_dot(painter, s, s.dot_size, s.color)
    else:
        _draw_cross(painter, s)

    if s.style != "dot" and s.center_dot and s.dot_size > 0:
        _draw_dot(painter, s, s.dot_size, s.dot_color)

    painter.end()
    return pixmap


def logical_size(s: CrosshairSettings, dpr: float = 1.0) -> tuple:
    scale = max(dpr, 1.0)
    half = _half_extent(s)
    side = max(int(math.ceil(2 * (half * scale + 4))), 1)
    return side / scale, side / scale


def render_icon(s: CrosshairSettings, size: int = 64) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    half = size / 2.0
    t = max(2, size // 8)
    ln = size // 3
    color = QColor(s.color)
    painter.setPen(QPen(color, t, Qt.SolidLine, Qt.RoundCap))
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        painter.drawLine(half, half, half + dx * ln, half + dy * ln)
    painter.setPen(Qt.NoPen)
    painter.setBrush(color)
    painter.drawEllipse(QRectF(half - t, half - t, 2 * t, 2 * t))
    painter.end()
    return pixmap
