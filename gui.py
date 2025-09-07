# jarvis_hud.py
# PyQt6 J.A.R.V.I.S-style dynamic HUD prototype
# Loads background image, draws AI face with pulsing eyes,
# animated network nodes/edges, particle trails, and live data overlays.

import math
import random
import sys
from dataclasses import dataclass
from typing import List, Tuple

from PyQt6.QtCore import (
    QEasingCurve,
    QPointF,
    QRectF,
    QLineF,
    QPropertyAnimation,
    QParallelAnimationGroup,
    QTimer,
    Qt,
)
from PyQt6.QtGui import (
    QAction,
    QColor,
    QConicalGradient,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QMainWindow,
    QWidget,
)

BACKGROUND_PATH = "image.jpg"  # change if needed

# ---------- Utility ----------

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def pulse(ticks: int, period_ms: int, min_v: float, max_v: float) -> float:
    # triangular pulse 0..1..0 mapped to min..max
    phase = (ticks % period_ms) / period_ms
    x = 2 * phase if phase <= 0.5 else 2 * (1 - phase)
    return lerp(min_v, max_v, x)

# ---------- Data classes ----------

@dataclass
class Node:
    pos: QPointF
    phase: float
    radius: float
    color: QColor

@dataclass
class Edge:
    a: int
    b: int
    dash_offset: float
    color: QColor

@dataclass
class Particle:
    pos: QPointF
    vel: QPointF
    life: float
    max_life: float
    hue: float

# ---------- Main HUD Widget ----------

class JarvisHUD(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.bg = QPixmap(BACKGROUND_PATH)
        self.ticks = 0
        self.setMinimumSize(1100, 650)

        # Nodes and edges
        random.seed(7)
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self._init_graph()

        # Particles
        self.particles: List[Particle] = []

        # Animation timer (60 FPS target)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(16)  # ~60fps

        # Data overlay timer
        self.uptime_ms = 0
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(lambda: setattr(self, "uptime_ms", self.uptime_ms + 1000))
        self.data_timer.start(1000)

        # Subtle widget opacity ramp on start (example of property animation)
        self._fade_in()

    # ---------- Initialization ----------

    def _init_graph(self):
        w, h = 1200, 700
        # Place nodes in bands to resemble a hemispherical grid
        for band in range(5):
            y = 260 + band * 70
            count = 6 + band * 2
            for i in range(count):
                x = 150 + i * (800 / max(1, count - 1)) + random.uniform(-20, 20)
                r = random.uniform(3, 6)
                hue = random.randint(180, 200)  # cyan-blue
                self.nodes.append(
                    Node(QPointF(x, y + random.uniform(-10, 10)), random.random(), r, QColor.fromHsl(hue, 255, 180))
                )
        # Connect near neighbors
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                if QLineF(self.nodes[i].pos, self.nodes[j].pos).length() < 180 and random.random() < 0.35:
                    self.edges.append(Edge(i, j, random.uniform(0, 100), QColor(0, 255, 255, 140)))

    def _fade_in(self):
        eff = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(eff)
        a = QPropertyAnimation(eff, b"opacity", self)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        a.setDuration(1200)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.start()

    # ---------- Animation update ----------

    def _emit_particles(self, center: QPointF, count: int = 8):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.8, 2.2)
            vel = QPointF(math.cos(angle) * speed, math.sin(angle) * speed)
            life = random.uniform(0.8, 1.6)
            hue = random.uniform(180, 195)
            self.particles.append(Particle(center, vel, life, life, hue))

    def _tick(self):
        self.ticks += 16

        # Slight node drift and blinking
        for n in self.nodes:
            n.phase += 0.02
            n.pos.setX(n.pos.x() + math.sin(n.phase) * 0.15)
            n.pos.setY(n.pos.y() + math.cos(n.phase * 0.6) * 0.10)

        # Animate dashed offsets for edges (gives moving pulses)
        for e in self.edges:
            e.dash_offset = (e.dash_offset + 1.6) % 100.0

        # Spawn particles near the center emitter
        center = QPointF(self.width() / 2, self.height() / 2 + 30)
        if random.random() < 0.6:
            self._emit_particles(center, count=random.randint(3, 6))

        # Update particles
        dt = 0.016
        alive: List[Particle] = []
        for p in self.particles:
            p.life -= dt
            if p.life > 0:
                # Curving motion toward center (attractor)
                to_c = center - p.pos
                d = math.hypot(to_c.x(), to_c.y()) + 1e-3
                acc = to_c * (0.02 / d)
                p.vel += acc
                p.pos += p.vel
                alive.append(p)
        self.particles = alive

        self.update()

    # ---------- Drawing ----------

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Background
        if not self.bg.isNull():
            painter.drawPixmap(self.rect(), self.bg)  # fit background
        else:
            painter.fillRect(self.rect(), QColor(8, 12, 22))

        # Dim vignette
        vg = QRadialGradient(QPointF(self.width() / 2, self.height() / 2), max(self.width(), self.height()) * 0.75)
        vg.setColorAt(0.0, QColor(0, 0, 0, 0))
        vg.setColorAt(1.0, QColor(0, 0, 0, 160))
        painter.fillRect(self.rect(), vg)

        # Network edges
        for e in self.edges:
            a = self.nodes[e.a].pos
            b = self.nodes[e.b].pos
            pen = QPen(e.color, 1.4)
            pen.setDashPattern([6, 10])
            pen.setDashOffset(e.dash_offset)
            painter.setPen(pen)
            painter.drawLine(a, b)

            # traveling light along edge
            t = ((self.ticks * 0.12 + e.dash_offset) % 100) / 100.0
            pt = QPointF(lerp(a.x(), b.x(), t), lerp(a.y(), b.y(), t))
            rg = QRadialGradient(pt, 10)
            c = QColor(120, 255, 255, 180)
            rg.setColorAt(0.0, c)
            rg.setColorAt(1.0, QColor(120, 255, 255, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(rg)
            painter.drawEllipse(pt, 8, 8)

        # Nodes (with glow using radial gradient)
        for n in self.nodes:
            glow_r = n.radius * 6
            rg = QRadialGradient(n.pos, glow_r)
            base = QColor(0, 255, 255, 180)
            base.setHsl(n.color.hslHue(), 255, 160, 180)
            rg.setColorAt(0.0, base)
            rg.setColorAt(1.0, QColor(base.red(), base.green(), base.blue(), 0))
            painter.setBrush(rg)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(n.pos, glow_r, glow_r)

            # core
            blink = 0.6 + 0.4 * math.sin(self.ticks * 0.01 + n.phase * 6.28)
            core = QColor(200, 255, 255, int(220 * blink))
            painter.setBrush(core)
            painter.setPen(QPen(QColor(170, 255, 255, 200), 1))
            painter.drawEllipse(n.pos, n.radius + 1.0, n.radius + 1.0)

        # Particle system (simple additive glow)
        for p in self.particles:
            alpha = int(255 * (p.life / p.max_life))
            col = QColor.fromHsl(int(p.hue), 255, 200, alpha)
            rg = QRadialGradient(p.pos, 12)
            rg.setColorAt(0.0, col)
            rg.setColorAt(1.0, QColor(col.red(), col.green(), col.blue(), 0))
            painter.setBrush(rg)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(p.pos, 12, 12)

        # Central AI face and pulsing eyes
        self._draw_ai_face(painter)

        # Data overlays
        self._draw_hud_text(painter)

    def _draw_ai_face(self, painter: QPainter):
        cx, cy = self.width() / 2, self.height() / 2 - 20

        # Face outline via path (stylized mask)
        path = QPainterPath(QPointF(cx - 140, cy - 120))
        path.cubicTo(cx - 120, cy - 190, cx + 120, cy - 190, cx + 140, cy - 120)
        path.cubicTo(cx + 150, cy - 20, cx + 90, cy + 80, cx, cy + 120)
        path.cubicTo(cx - 90, cy + 80, cx - 150, cy - 20, cx - 140, cy - 120)

        pen = QPen(QColor(120, 255, 255, 200), 2.0)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Nose and mouth strokes
        small = QPainterPath()
        small.moveTo(cx, cy - 10)
        small.lineTo(cx, cy + 25)
        small.moveTo(cx - 10, cy + 26)
        small.cubicTo(cx, cy + 36, cx, cy + 36, cx + 10, cy + 26)
        painter.drawPath(small)

        # Eyes
        eye_dx, eye_y = 70, cy - 40
        eye_r = 16
        for sign in (-1, 1):
            center = QPointF(cx + sign * eye_dx, eye_y)
            # outer glow
            glow = QRadialGradient(center, 36)
            glow.setColorAt(0.0, QColor(100, 255, 255, 160))
            glow.setColorAt(1.0, QColor(100, 255, 255, 0))
            painter.setBrush(glow)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, 34, 34)

            # iris core with pulse
            pulse_a = pulse(self.ticks, 1200, 0.55, 1.0)
            iris = QColor(180, 255, 255, int(255 * pulse_a))
            painter.setBrush(iris)
            painter.setPen(QPen(QColor(200, 255, 255, 220), 1.2))
            painter.drawEllipse(center, eye_r, eye_r)

            # scanning slit
            slit_w = 3 + 6 * pulse(self.ticks + 300, 1600, 0.0, 1.0)
            painter.setPen(QPen(QColor(255, 255, 255, 200), 1.0))
            painter.drawLine(QPointF(center.x() - 10, center.y()),
                             QPointF(center.x() + 10, center.y()))
            painter.setPen(QPen(QColor(180, 255, 255, 180), slit_w))
            painter.drawPoint(center)

        # Halo ring with rotating conical gradient
        radius = 64
        cg = QConicalGradient(QPointF(cx, cy + 88), (self.ticks * 0.04) % 360)
        cg.setColorAt(0.00, QColor(120, 255, 255, 0))
        cg.setColorAt(0.10, QColor(120, 255, 255, 180))
        cg.setColorAt(0.20, QColor(120, 255, 255, 0))
        painter.setPen(QPen(QColor(120, 255, 255, 180), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy + 88), radius, radius)

        # vertical beam
        beam_h = 180
        lg = QLinearGradient(QPointF(cx, cy + 88 - beam_h / 2), QPointF(cx, cy + 88 + beam_h / 2))
        lg.setColorAt(0.0, QColor(120, 255, 255, 0))
        lg.setColorAt(0.5, QColor(120, 255, 255, 140))
        lg.setColorAt(1.0, QColor(120, 255, 255, 0))
        painter.fillRect(QRectF(cx - 1.2, cy + 88 - beam_h / 2, 2.4, beam_h), lg)

    def _draw_hud_text(self, painter: QPainter):
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setPen(QColor(160, 220, 255))

        # Title
        font = QFont("Segoe UI", 18, QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.drawText(30, 46, "J.A.R.V.I.S NETWORK INTERFACE")

        # Stats bar
        small = QFont("Consolas", 11)
        painter.setFont(small)
        uptime = self.uptime_ms // 1000
        msgs = [
            f"UPTIME: {uptime:05d}s",
            f"NODES: {len(self.nodes)}",
            f"EDGES: {len(self.edges)}",
            f"PARTICLES: {len(self.particles)}",
            f"FPS ~ 60",
        ]
        x = 30
        for m in msgs:
            painter.drawText(x, self.height() - 30, m)
            x += painter.fontMetrics().horizontalAdvance(m + "    ")

        # Mini bar charts
        base_y = self.height() - 60
        base_x = 30
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(24):
            h = 6 + 26 * (0.3 + 0.7 * random.random())
            alpha = 120 + int(100 * math.sin((self.ticks * 0.01 + i) * 0.2))
            painter.setBrush(QColor(120, 255, 255, alpha))
            painter.drawRect(int(base_x + i * 10), int(base_y - h), int(6), int(h))

# ---------- Window ----------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S HUD - PyQt6")
        self.hud = JarvisHUD(self)
        self.setCentralWidget(self.hud)
        self.resize(1200, 700)

        # Toggle particles action
        toggle = QAction("Toggle Particles", self)
        toggle.setCheckable(True)
        toggle.setChecked(True)
        toggle.triggered.connect(self.toggle_particles)
        self.menuBar().addAction(toggle)

    def toggle_particles(self, checked: bool):
        if checked and not self.hud.timer.isActive():
            self.hud.timer.start(16)
        elif not checked and self.hud.timer.isActive():
            self.hud.timer.stop()

# ---------- Entrypoint ----------

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
