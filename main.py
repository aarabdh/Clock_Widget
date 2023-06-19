from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient, QConicalGradient
from PyQt5.QtCore import QRectF, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QMenu, QAction, QGraphicsDropShadowEffect, QToolButton
import time
import sys

class TransparentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mult = 1
        self.setWindowOpacity(0.5)
        self.darkflag = False

        self.setGeometry(1920-150, 100, 110*self.mult, 150*self.mult)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.time_label = QLabel(central_widget)
        self.time_label.setGeometry(5, 5, 100*self.mult, 100*self.mult)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("QLabel { color: white; font-size: 24px; }")

        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setColor(QColor(0, 0, 0, 220))
        shadow_effect.setOffset(QPoint(1, 1))
        shadow_effect.setBlurRadius(4)

        self.time_label.setGraphicsEffect(shadow_effect)

        # Create a button
        self.close_button = QToolButton(central_widget)
        self.close_button.setGeometry(45,125, 20*self.mult, 20*self.mult)
        self.close_button.setText("X")
        self.close_button.setFont(QFont("Arial", 12*self.mult, QFont.Bold))
        self.close_button.clicked.connect(self.close)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateShapes)
        self.timer.start(5)

        self.context_menu = QMenu(self)
        self.create_actions()
        self.context_menu.addAction(self.action1)
        self.context_menu.addAction(self.action2)
        self.stylesheet = """
            QMenu::item {
                padding: 3px 20px 3px 10px;
                icon-size: 0px;
            }
            
            QMenu::item:selected {
                background-color: #b3d4fc;
            }
            
            QMenu::item:hover {
                background-color: #f0f0f0;
            }
        """
        self.context_menu.setStyleSheet(self.stylesheet)

        self.sec = time.localtime().tm_sec
        self.hour = time.localtime().tm_hour
        self.min = time.localtime().tm_min
        self.milsec = int((time.time() % 1)*1000)

        self.dragging = False
        self.drag_start_pos = None

        self.time_label.setText(f"{self.hour:02d}:{self.min:02d}")

        self.window_opacity = 0.5

    def create_actions(self):
        if self.darkflag:
            self.action1 = QAction("Light Clock", self)
            self.action1.triggered.connect(self.handle_action1)
        else:
            self.action1 = QAction("Dark Clock", self)
            self.action1.triggered.connect(self.handle_action1)
        if self.mult == 1:
            self.action2 = QAction("Increase Size by 1.5", self)
            self.action2.triggered.connect(self.handle_action2)
        else:
            self.action2 = QAction("Decrease Size by 1.5", self)
            self.action2.triggered.connect(self.handle_action2)
    
    def handle_action1(self):
        self.darkflag = not self.darkflag
        self.create_actions()
        self.context_menu.clear()
        self.context_menu.addAction(self.action1)
        self.context_menu.addAction(self.action2)
        self.context_menu.setStyleSheet(self.stylesheet)

    def handle_action2(self):
        if self.mult == 1:
            self.mult = 1.5
        else:
            self.mult = 1
        self.setGeometry(self.x(), self.y(), int(110*self.mult), int(150*self.mult))
        self.close_button.setGeometry(int(45*self.mult),int(125*self.mult), int(20*self.mult), int(20*self.mult))
        self.create_actions()
        self.context_menu.clear()
        self.context_menu.addAction(self.action1)
        self.context_menu.addAction(self.action2)
        self.context_menu.setStyleSheet(self.stylesheet)

    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_start_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

    def enterEvent(self, event):
        self.window_opacity = 1.0
        self.setWindowOpacity(self.window_opacity)

    def leaveEvent(self, event):
        self.window_opacity = 0.5
        self.setWindowOpacity(self.window_opacity)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        scaled_arc_rect = QRectF(5, 5, 100*self.mult, 100*self.mult)
        gradient = QConicalGradient(scaled_arc_rect.center(), 90)

        gradient.setColorAt(0, Qt.red)
        gradient.setColorAt(0.25, Qt.blue)
        gradient.setColorAt(0.5, Qt.cyan)
        gradient.setColorAt(0.75, Qt.blue)
        gradient.setColorAt(1.0, Qt.red)

        painter.setPen(QPen(gradient, 4))
        angle = (self.sec%60 +1)*360//60
        gradient.setAngle(angle)
        painter.drawArc(scaled_arc_rect, 90 * 16, -angle * 16 - int(16* 6 * self.milsec))

    def updateShapes(self):
        current_time = time.localtime()
        self.sec = current_time.tm_sec
        self.min = current_time.tm_min
        self.hour = current_time.tm_hour
        self.milsec = (time.time() % 1)
        self.time_label.setText(f"{self.hour:02d}:{self.min:02d}")

        self.time_label.setGeometry(5, 5, int(100*self.mult), int(100*self.mult))
        self.time_label.setAlignment(Qt.AlignCenter)

        if self.darkflag:
            self.time_label.setStyleSheet("QLabel { color: black; font-size: "+str(int(24*self.mult))+"px; }")
        else:
            self.time_label.setStyleSheet("QLabel { color: white; font-size: "+str(int(24*self.mult))+"px; }")

        self.update()

    def closeEvent(self, event):
        self.timer.stop()
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransparentWindow()
    window.show()
    sys.exit(app.exec())
